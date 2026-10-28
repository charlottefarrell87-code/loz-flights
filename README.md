# Loz flights

Private, password-protected copy of the **Loz Flights** tracker: every saved fare search and its dashboard, read-only. Searches are created, edited and deleted in the tracker in Claude; prices are checked on Google Flights every Tuesday and Friday and this page is rebuilt each time.

`index.html` is encrypted (AES-256-GCM, key from PBKDF2-SHA256 with 600,000 iterations), so nothing can be read without the password. `template.html` (the tracker page), `lock.html` and `build.py` hold no fare data.

Editing on the site: "Connect GitHub to edit" asks for a fine-grained token (this repository only, Contents: Read and write), kept in that browser. Ticking "Share editing with everyone who has the page password" saves that token in `shared-token.enc.json`, encrypted with the page password, so password holders can edit without a GitHub account. Saved, edited, paused or deleted searches are encrypted with the page password into `pending.enc.json`; the twice-weekly check applies them to the tracker (`python3 pending.py read|clear PASSWORD`) and clears the file.

Rebuild: `python3 build.py data.json PASSWORD index.html`, where `data.json` is `{"searches": [...], "checks": {...}}` exported from the tracker. Never commit `data.json`.
