"""Build the password-protected Loz Flights page.

Usage: python3 build.py data.json PASSWORD out/index.html

data.json is {"searches": [{"id": ..., "data": {...criteria...}}],
              "checks": {"<search id>": [{"checked": "YYYY-MM-DD", "rows": [...]}]}}
exported from the Loz Flights tracker in Claude. The page is template.html (the
tracker's own page) shown read-only with that data, encrypted with AES-256-GCM
(key from PBKDF2-SHA256 over the password) inside lock.html.
Only the encrypted index.html is ever committed; never commit data.json.
"""
import base64, json, os, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600_000
here = Path(__file__).parent
data_path, password, out_path = sys.argv[1], sys.argv[2], Path(sys.argv[3])

data = json.loads(Path(data_path).read_text())
assert isinstance(data.get("searches"), list) and isinstance(data.get("checks"), dict), "data.json needs searches and checks"
payload_js = json.dumps(data).replace("</", "<\\/")
body = (here / "template.html").read_text()
page = (
    '<!doctype html><html lang="en-GB"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    '<meta name="robots" content="noindex, nofollow">'
    "<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}"
    ".lockbar{max-width:1120px;margin:0 auto 32px;padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px));"
    "font:12px/1.5 system-ui,sans-serif;color:var(--muted,#667)}.lockbar button{font:inherit;background:none;border:1px solid var(--line,#ccd);"
    "color:inherit;border-radius:6px;padding:3px 10px;cursor:pointer;margin-left:8px}</style>"
    f"</head><body><script>window.LOZ_DATA = {payload_js};</script>\n{body}\n"
    '<p class="lockbar">Prices from Google Flights, indicative and may change at booking. Read-only copy; manage searches in Claude.'
    '<button type="button" id="lockBtn">Lock this device</button></p>'
    "<script>document.getElementById('lockBtn').addEventListener('click',()=>{try{localStorage.removeItem('loz-key')}catch(e){}location.reload()});</script>"
    "</body></html>"
)

# The salt stays the same between builds (salt.b64, committed) so a device that ticked
# "Remember on this device" keeps working after each fare check. It is not secret.
salt_file = here / "salt.b64"
if salt_file.exists():
    salt = base64.b64decode(salt_file.read_text().strip())
else:
    salt = os.urandom(16)
    salt_file.write_text(base64.b64encode(salt).decode() + "\n")
iv = os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())
ct = AESGCM(key).encrypt(iv, page.encode(), None)
b = lambda x: base64.b64encode(x).decode()
lock = (here / "lock.html").read_text().replace("__PAYLOAD__", json.dumps({"salt": b(salt), "iv": b(iv), "iter": ITER, "ct": b(ct)}))
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(lock)
n = sum(len(c.get("rows", [])) for cs in data["checks"].values() for c in cs)
print(f"Wrote {out_path} ({out_path.stat().st_size} bytes, {len(data['searches'])} searches, {n} fare rows)")
