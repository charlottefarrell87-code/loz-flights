"""Read or clear dashboard feedback sent from the Loz Flights site.

The site's Feedback button encrypts suggestions with the page password (same key as
pending.enc.json) and commits them to feedback.enc.json as {"v": 1, "iv": ..., "ct": ...}.

  python3 feedback.py read  PASSWORD   # prints {"items": [...]} as JSON
  python3 feedback.py clear PASSWORD   # rewrites feedback.enc.json with no items

Each item is {"at", "name", "text", "search", "from"}. Feedback sent from the tracker
in Claude is kept in its database instead, in the "feedback" collection.
"""
import base64, json, os, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

here = Path(__file__).parent
cmd, password = sys.argv[1], sys.argv[2]
path = here / "feedback.enc.json"
salt = base64.b64decode((here / "salt.b64").read_text().strip())
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600_000).derive(password.encode())

if cmd == "read":
    if not path.exists():
        print(json.dumps({"items": []}))
    else:
        doc = json.loads(path.read_text())
        data = json.loads(AESGCM(key).decrypt(base64.b64decode(doc["iv"]), base64.b64decode(doc["ct"]), None)) if doc.get("ct") else {"items": []}
        print(json.dumps(data, indent=1))
elif cmd == "clear":
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, json.dumps({"items": []}).encode(), None)
    path.write_text(json.dumps({"v": 1, "iv": base64.b64encode(iv).decode(), "ct": base64.b64encode(ct).decode()}))
    print("Cleared feedback.enc.json")
else:
    sys.exit("Use: feedback.py read|clear PASSWORD")
