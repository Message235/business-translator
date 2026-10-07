# Deployment

Frontend (Next.js) auf Vercel, Backend (FastAPI) auf Heroku.

| Teil | URL |
| --- | --- |
| Frontend | https://business-translator.vercel.app |
| Backend | https://business-translator-api-75a8fdbc26c1.herokuapp.com |

CORS läuft über `FRONTEND_ORIGIN` (Backend), die API-URL im Frontend über `NEXT_PUBLIC_API_URL`.

## 1. Backend auf Heroku (zuerst, damit die URL bekannt ist)

Heroku erwartet die App im Repo-Root, hier liegt sie in `backend/`. Dafür gibt es `backend/Procfile` und `backend/.python-version` (`.python-version` ersetzt das veraltete `runtime.txt`).

```bash
heroku login
heroku create business-translator-api
heroku config:set OPENROUTER_API_KEY=sk-... -a business-translator-api
heroku config:set FRONTEND_ORIGIN=https://business-translator.vercel.app -a business-translator-api
git subtree push --prefix backend heroku main
```

- `backend/.env` nicht committen, Werte nur als Config Vars setzen. Optional: `OPENROUTER_MODEL`, `RATE_LIMIT`.
- Test: `curl https://business-translator-api-75a8fdbc26c1.herokuapp.com/api/health`
- Schlägt `git subtree push` mit "Authentication failed" fehl, den Heroku-Token als Header mitgeben (Bash):

  ```bash
  B=$(printf ':%s' "$(heroku auth:token)" | base64 -w0)
  git -c "http.extraheader=Authorization: Basic $B" subtree push --prefix backend heroku main
  ```

## 2. Frontend auf Vercel

Die Vercel-Anbindung ans GitHub-Repo besteht nicht (Vercel-GitHub-App ohne Zugriff), daher gibt es kein Auto-Deploy bei `git push`. Deployt wird per CLI aus `frontend/`:

```bash
cd frontend
npx vercel login                      # einmalig, Browser-Login
npx vercel link --yes --project business-translator
printf 'https://business-translator-api-75a8fdbc26c1.herokuapp.com' | npx vercel env add NEXT_PUBLIC_API_URL production
npx vercel deploy --prod --yes
```

`NEXT_PUBLIC_*` wird beim Build eingebacken. Nach einer Änderung der Variable muss neu deployt werden. Die URL ohne Slash am Ende angeben.

Alternativ per Dashboard: Repo importieren, **Root Directory** auf `frontend` setzen, `NEXT_PUBLIC_API_URL` eintragen.

## 3. Verbinden prüfen

```bash
# CORS-Preflight (muss Access-Control-Allow-Origin mit der Vercel-Domain liefern)
curl -i -X OPTIONS \
  -H "Origin: https://business-translator.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  https://business-translator-api-75a8fdbc26c1.herokuapp.com/api/translate
```

Mehrere Origins (z. B. zusätzlich eine Custom Domain) gehen kommagetrennt in `FRONTEND_ORIGIN`.

## Updates

- Backend: `git subtree push --prefix backend heroku main`
- Frontend: `npx vercel deploy --prod --yes` in `frontend/`
