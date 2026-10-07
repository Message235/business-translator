# Deployment

Frontend (Next.js) auf Vercel, Backend (FastAPI) auf Heroku.

Das Projekt ist bereits vorbereitet: CORS läuft über `FRONTEND_ORIGIN`, die API-URL im Frontend über `NEXT_PUBLIC_API_URL`. Fürs Backend fehlen nur eine `Procfile` und eine `runtime.txt`.

## 1. Backend auf Heroku (zuerst, damit die URL bekannt ist)

Heroku erwartet die App im Repo-Root, hier liegt sie in `backend/`. Deshalb `git subtree`:

```bash
# im Repo-Root
echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > backend/Procfile
echo "python-3.12.x" > backend/runtime.txt   # exakte Version prüfen, z. B. python-3.12.8
git add backend && git commit -m "Add Heroku Procfile"

heroku login
heroku create dein-app-name
heroku config:set OPENROUTER_API_KEY=sk-... -a dein-app-name
heroku config:set FRONTEND_ORIGIN=https://dein-projekt.vercel.app -a dein-app-name   # kann nach Schritt 2 gesetzt werden
git subtree push --prefix backend heroku main
```

- `backend/.env` nicht committen, Werte nur als Config Vars setzen. Optional: `OPENROUTER_MODEL`, `RATE_LIMIT`.
- Test: `https://dein-app-name.herokuapp.com/api/health`
- Dev-Pakete in `requirements.txt` (`pytest`, `httpx`) sind für Heroku unschädlich.

## 2. Frontend auf Vercel

1. Repo auf GitHub pushen und auf vercel.com importieren.
2. **Root Directory** auf `frontend` setzen (Next.js wird automatisch erkannt).
3. Environment Variable setzen: `NEXT_PUBLIC_API_URL=https://dein-app-name.herokuapp.com` (ohne Slash am Ende).
4. Deployen.

## 3. Verbinden

Nach dem ersten Vercel-Deploy die echte Domain als CORS-Origin setzen:

```bash
heroku config:set FRONTEND_ORIGIN=https://dein-projekt.vercel.app -a dein-app-name
```

Mehrere Origins gehen kommagetrennt (z. B. zusätzlich eine Custom Domain).

`NEXT_PUBLIC_*` wird beim Build eingebacken. Nach einer Änderung der Variable muss in Vercel neu deployt werden.
