"""Read or clear searches saved on the Loz Flights site.

The site encrypts changes with the page password (same key as index.html: PBKDF2-SHA256
over the password with salt.b64, 600,000 iterations, AES-256-GCM) and commits them to
pending.enc.json as {"v": 1, "iv": ..., "ct": ...}.

  python3 pending.py read  PASSWORD   # prints {"changes": [...]} as JSON
  python3 pending.py clear PASSWORD   # rewrites pending.enc.json with no changes

Each change is {"op": "upsert", "id", "name", "data": {...search...}, "at"}
or {"op": "delete", "id", "name", "at"}. Apply them in order, then clear.
"""
import base64, json, os, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

here = Path(__file__).parent
cmd, password = sys.argv[1], sys.argv[2]
path = here / "pending.enc.json"
salt = base64.b64decode((here / "salt.b64").read_text().strip())
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600_000).derive(password.encode())

if cmd == "read":
    if not path.exists():
        print(json.dumps({"changes": []}))
    else:
        doc = json.loads(path.read_text())
        data = json.loads(AESGCM(key).decrypt(base64.b64decode(doc["iv"]), base64.b64decode(doc["ct"]), None)) if doc.get("ct") else {"changes": []}
        print(json.dumps(data, indent=1))
elif cmd == "clear":
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, json.dumps({"changes": []}).encode(), None)
    path.write_text(json.dumps({"v": 1, "iv": base64.b64encode(iv).decode(), "ct": base64.b64encode(ct).decode()}))
    print("Cleared pending.enc.json")
else:
    sys.exit("Use: pending.py read|clear PASSWORD")
