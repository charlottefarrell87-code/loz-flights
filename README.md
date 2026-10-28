# Loz flights

Private, password-protected page tracking return fares to Melbourne from Europe (land by 24 Jan 2027, back in the UK by 26 Apr 2027). Prices are checked on Google Flights every Tuesday and Friday.

`index.html` is encrypted (AES-256-GCM, key from PBKDF2-SHA256 with 600,000 iterations), so the fares can only be read with the password. `template.html`, `lock.html` and `build.py` hold no fare data.

Rebuild: `python3 build.py fares.json PASSWORD index.html` (never commit `fares.json`).
