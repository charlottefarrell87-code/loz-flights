# Loz flights

Private, password-protected copy of the **Loz Flights** tracker: every saved fare search and its dashboard, read-only. Searches are created, edited and deleted in the tracker in Claude; prices are checked on Google Flights every Tuesday and Friday and this page is rebuilt each time.

`index.html` is encrypted (AES-256-GCM, key from PBKDF2-SHA256 with 600,000 iterations), so nothing can be read without the password. `template.html` (the tracker page), `lock.html` and `build.py` hold no fare data.

Rebuild: `python3 build.py data.json PASSWORD index.html`, where `data.json` is `{"searches": [...], "checks": {...}}` exported from the tracker. Never commit `data.json`.
