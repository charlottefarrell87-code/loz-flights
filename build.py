"""Build the password-protected Loz flights page.

Usage: python3 build.py fares.json PASSWORD out/index.html

Renders template.html with the fares, encrypts the result with AES-256-GCM
(key from PBKDF2-SHA256 over the password), and writes it into lock.html.
Only the encrypted page should ever be committed; never commit fares.json.
"""
import base64, json, os, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600_000
here = Path(__file__).parent
fares_path, password, out_path = sys.argv[1], sys.argv[2], Path(sys.argv[3])

fares = json.loads(Path(fares_path).read_text())
page = (here / "template.html").read_text().replace("__FARES__", json.dumps(fares).replace("</", "<\\/"))

salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())
ct = AESGCM(key).encrypt(iv, page.encode(), None)
b = lambda x: base64.b64encode(x).decode()
payload = json.dumps({"salt": b(salt), "iv": b(iv), "iter": ITER, "ct": b(ct)})

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text((here / "lock.html").read_text().replace("__PAYLOAD__", payload))
print(f"Wrote {out_path} ({out_path.stat().st_size} bytes, {len(fares)} fare rows)")
