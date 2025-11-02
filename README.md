# CatchProbe Email Triage Platform

This workspace bundles a FastAPI microservice that triages submitted email files together with a React/Tailwind upload interface tailored for CatchProbe analysts.

## Project Layout

```
packages/
  backend/    # FastAPI application, adapters and pytest suite
  frontend/   # Vite + React single-page upload UI (Turkce copy)
docker-compose.yml
README.md
```

## Backend Highlights (`packages/backend`)

- Parses `.eml` and `.msg` using `mailparser`/`extract_msg`
- SPF/DKIM/DMARC evaluation, IOC extraction, URL HEAD expansion, deterministic mock VirusTotal verdicts
- YARA scanning with hot-reloadable rule directory
- Endpoints
  - `POST /ingest` (header `X-API-KEY`)
  - `POST /catchprobe/ingest` (header `X-CATCHPROBE-APIKEY`)
  - `POST /catchprobe/callback`
  - `GET /report/{ticket_id}`
  - `GET /artifact/{sha256}`
- Reports and artefacts persisted under `storage/` (configurable)
- Optional report push with HMAC signature (`X-REPORT-SIGNATURE`)

### Backend Environment

Defined in `packages/backend/.env.example`:

| Variable | Purpose |
| --- | --- |
| `TRIAGE_API_KEYS` | Comma separated ingest keys |
| `TRIAGE_CATCHPROBE_API_KEYS` | Comma separated CatchProbe keys |
| `TRIAGE_REPORT_BASE_DIR` | Storage root for reports and artefacts |
| `TRIAGE_URL_HEAD_TIMEOUT_SECONDS` | HEAD request timeout |
| `TRIAGE_REPORT_WEBHOOK_URL` / `TRIAGE_REPORT_WEBHOOK_SECRET` | Optional push target |

## Frontend Highlights (`packages/frontend`)

- Vite + React + TypeScript + TailwindCSS
- Drag & Drop and file picker for `.eml` / `.msg` (20 MB limit)
- Client-side SHA-256 hashing (Web Crypto), Turkish copy, accessible labels
- Per-file progress, cancel via `AbortController`, queue states, toast notifications
- Report cards with classification badges, IOC chips, attachment/YARA/VT summaries, copy/download/preview actions
- Dark mode toggle (`prefers-color-scheme` aware)
- Tests with Vitest + React Testing Library for `UploadZone` and `ReportCard`

### Frontend Environment

`packages/frontend/.env.example` lists:

| Variable | Purpose |
| --- | --- |
| `VITE_API_BASE_URL` | Backend base URL (default `http://localhost:8000`) |
| `VITE_DEFAULT_ENDPOINT` | `direct` or `catchprobe` upload target |
| `VITE_REQUIRE_API_KEY` | Enforce API key input in UI |

## Running Locally

### With Docker Compose

```bash
docker-compose up --build
```

- Backend => http://localhost:8000 (docs at `/docs`)
- Frontend => http://localhost:8080

### Manual Development

Backend:

```bash
cd packages/backend
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd packages/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## Testing

```bash
# Backend
cd packages/backend
pytest

# Frontend
cd ../frontend
npm run test
```

Backend tests cover ingest success, API key validation, file size limits and artefact retrieval. Frontend smoke tests mock Web Crypto/clipboard to validate drag & drop flows and report rendering.

## Deployment Notes

- `packages/backend/Dockerfile` builds a slim Python image served via Uvicorn
- `packages/frontend/Dockerfile` compiles static assets and serves them with nginx
- `docker-compose.yml` exposes backend port `8000` and frontend port `8080`, persisting backend storage in the `backend-data` volume

## Troubleshooting

- Missing API key headers return `401` with JSON error payload
- Payloads over 20 MB return `413`
- URL expansion failures are logged but do not fail triage; reports flag the URL as unresolved
- Run `docker-compose down -v` to clear stored artefacts/reports during development

## License

Internal CatchProbe engineering use only.

