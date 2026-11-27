# Farmer Assistant: MVP (Phases 1 and 2)

A web chat simulator and development dashboard for the Farmer Assistant chatbot (weather, crop rates,
credit, certifications and Ask Anything), backed by FastAPI and PostgreSQL with dummy data.
The conversation engine is channel-independent, so WhatsApp Business Cloud API can be added
later as a thin adapter without changing the chatbot logic.

```
frontend/  React + Vite + TypeScript + Tailwind (chat simulator, dashboard)
backend/   FastAPI + SQLAlchemy + PostgreSQL (conversation engine, services, APIs)
```

---

## 1. Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12+ (tested on 3.13) | |
| Node.js | 20+ (tested on 22) | |
| PostgreSQL | 14+ | This machine runs PostgreSQL 18 on **port 5433** |

## 2. Database setup (once)

Create the database. On Windows, `psql` is not on PATH, so use the full path:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5433 -U postgres -c "CREATE DATABASE farmer_assistant;"
```

## 3. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env
# edit .env: set your postgres password in DATABASE_URL and a random IDENTITY_HASH_SECRET

python -m app.database.init_db          # create tables
python -m app.database.seed             # optional: 42 demo farmers for the dashboard
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs · Health: http://localhost:8000/api/health

Reset everything (drops all data): `python -m app.database.seed --reset`

### What is in the database, and how a teammate gets the same setup

- **Chatbot content** (districts, crop rates, credit, certifications, knowledge base) is **not** in the database. It is in
  `backend/app/data/*.json`, read at startup and shared through git: `git pull` gives a teammate the same content.
- **The database** holds only activity: farmers, consents, sessions, usage logs, feedback and WhatsApp message counts.
  `python -m app.database.seed` fills all of these with demo data (topic ids are taken from the JSON files, so the demo
  data always matches the current content).

A teammate's setup: clone, create the database, copy `backend/.env.example` to `.env` with their own PostgreSQL password,
then `pip install -r requirements.txt`, `python -m app.database.init_db` and `python -m app.database.seed`. Real farmer
activity from your machine is not copied (and should not be: it is personal data).

### Backend tests

Tests use an in-memory SQLite database, so PostgreSQL is not needed:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

## 4. Frontend

```powershell
cd frontend
npm install
copy .env.example .env      # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173.

| Route | Page |
|---|---|
| `/` | Public website: Home, plus `/about`, `/services`, `/timeline`, `/team`, `/contact` |
| `/chat` | Chat simulator |
| `/admin` | Admin dashboard (password-gated) - see section 9 |

Website copy (services, team members, timeline, FAQ, contact email) lives in `frontend/src/content/site.ts`.
The timeline marks each phase *Completed / In progress / Upcoming* automatically from today's date.

**WhatsApp button:** set `VITE_WHATSAPP_NUMBER` in `frontend/.env` to the bot's number in international format,
digits only (e.g. `923001234567`), and restart `npm run dev`. Every "Chat on WhatsApp" button then opens
`https://wa.me/<number>?text=Hi`, which starts the bot's welcome flow. While it is empty, the buttons open the web
chat simulator at `/chat` instead.

---

## 5. How to test the chatbot

1. Open **Chat simulator** (`/chat`) and click **Say “Hi”**. As a new farmer you are asked:
   - Q1: anonymous usage recording (Yes / No)
   - Q2: weekly farming updates (Yes / No)

   Either answer leads to the main menu.
2. **Weather** → pick a district. The 3-day forecast is live from [Open-Meteo](https://open-meteo.com) (set `WEATHER_PROVIDER=json` in `backend/.env` for the offline sample data, where *Khairpur* has rain).
3. **Crop Rates** → *Cotton* → *Ghotki*. Shows the rate, source, date, summer/winter trend and expected range.
4. **Credit Information** → *Benazir Hari Card*, or type `ztbl`.
5. **Certifications** → *Organic*.
6. **Ask Anything**, or just type at any time:
   - `When should I sow wheat?` → answered from the knowledge base
   - `How to control pink bollworm` → answered
   - `What is the price of gold?` → "not currently available" fallback
7. Under every answer, click **Yes, helpful** / **Not helpful**. The vote is saved in the `feedback` table.
8. Click **Home** (header or quick reply) or type `home`/`menu` at any point.
9. Click the **mic** button. A mock voice note is sent and the backend replies that voice isn't supported yet.
10. Click **Start as a new farmer** in the side panel to repeat onboarding with a fresh anonymous ID.
    Answer **No** to usage recording and confirm on the **Dashboard** that your clicks add no usage rows.

Typed replies work as well as buttons: `2`, `cotton`, `sukkur`, `yes`, `benazir`.

---

## 6. Architecture

```
React simulator ──► POST /api/chat ──► channels/web.py ──┐
(future) WhatsApp ─► webhook ────────► channels/whatsapp.py ┤   (Phase 3)
                                                          ▼
                    InboundMessage ─► ConversationService.handle() ─► ConversationResult
                                         │ state machine (conversation_sessions)
          ┌──────────────┬───────────────┼──────────────┬────────────────┬──────────────────┐
     WeatherService  CropService  CreditService  CertificationService  KnowledgeService  Consent/Usage/Feedback
          └─ JSON providers (swappable: Open-Meteo, Google Sheet, RAG) ─┘                     └─ repositories ─► PostgreSQL
```

| Path | Responsibility |
|---|---|
| `backend/app/domain/messages.py` | Channel-neutral `InboundMessage` / `OutboundMessage` / `Option`. Limits match WhatsApp (≤3 options = buttons, ≤10 = list, label ≤24 chars). |
| `backend/app/services/conversation_service.py` | State machine and routing. The **only** place chatbot decisions are made. |
| `backend/app/services/presenters.py` + `app/i18n/` | All wording, in English (`en`), Urdu (`ur`) and Sindhi (`sd`). Data files hold `{en, ur, sd}` values. New farmers pick a language first; it can be changed any time from the menu, by typing a language name, or with the switcher in the web chat header. |
| `backend/app/services/*_service.py` | Feature services returning structured data from swappable providers. |
| `backend/app/channels/web.py` | Web JSON ⇄ internal messages. |
| `backend/app/repositories/` | All SQL queries. |

### Database tables

| Table | Purpose |
|---|---|
| `farmer_consents` | Anonymous `farmer_id` (UUID), HMAC hash of the channel identifier (never the raw phone number), `usage_consent` and `weekly_updates` stored separately with timestamps, `language` and the remembered `district`. |
| `processed_messages` | HMAC hash of each inbound channel message id, so a redelivered webhook is not answered twice. Pruned after 8 days. |
| `outbound_message_counts` | Bot messages sent per channel per month (no farmer link), to track the WhatsApp free tier. |
| `conversation_sessions` | `state` + `context` (JSON) for multi-step flows. Expires after 30 minutes of inactivity. |
| `usage_logs` | Service/action/structured attributes. Written **only** when `usage_consent = true`. Free-text questions are never stored, only the matched topic id. |
| `feedback` | Helpful yes/no per answer (`response_id` unique). Always stored, but linked to the farmer only with consent. |

Withdrawing usage consent (via `POST /api/consent`) deletes that farmer's usage logs and unlinks their feedback.

### API

| Method | Path | Body / notes |
|---|---|---|
| POST | `/api/chat` | `{client_id, text?, option_id?, message_type: "text"\|"voice"}` → `{farmer_id, session_id, state, messages[]}` |
| GET | `/api/consent/{client_id}` | Current preferences (404 if unknown) |
| POST | `/api/consent` | `{client_id, usage_consent?, weekly_updates?}` |
| POST | `/api/feedback` | `{client_id, response_id, service, helpful}` (idempotent per response) |
| GET | `/api/dashboard/summary?days=7` | Totals, new/active farmers, service usage, feedback, consent, recent interactions |
| GET | `/api/dashboard/messages` | Bot messages sent this month per channel, and the WhatsApp free messages left |
| GET | `/api/health` | |

---

## 7. WhatsApp (Meta Cloud API)

The adapter is `backend/app/channels/whatsapp.py` and the webhook is `backend/app/api/whatsapp_webhook.py`
(`GET`/`POST /api/whatsapp/webhook`). The engine, services and database are the same as for the web simulator.

1. In `backend/.env` set `ACCESS_TOKEN`, `PHONE_NUMBER_ID`, `VERIFY_TOKEN` (any random string) and `APP_SECRET`
   (Meta app -> App settings -> Basic). Restart uvicorn.
2. Expose the backend over HTTPS: `ngrok http 8000` (the free URL changes on every restart).
3. Meta app -> WhatsApp -> Configuration: Callback URL `https://<tunnel>/api/whatsapp/webhook`, the same verify
   token, **Verify and save**, then subscribe to the **messages** field.
4. Send "Hi" to the test number from a phone added as a test recipient (API Setup -> "To", up to 5 numbers).

How it works: webhooks without a valid `X-Hub-Signature-256` are rejected; each message is handled during the request
(redeliveries with the same message id are ignored) and the replies are sent to the Graph API in a background task after
the 200 response. Answers carry `Yes, helpful` / `Not helpful` / `Home` buttons in the same message; up to 3 options
are reply buttons and 4-10 a list message. Send errors are logged with a hint (expired token, number not a test recipient).

Still to do for a pilot: a permanent System User token, the real phone number and display name, business verification,
a payment method, and approved message templates plus an `update_subscriptions` table for the weekly updates
(they are sent outside the 24-hour reply window).

## 8. Admin dashboard

`/admin` lets one operator update chatbot content and see farmer/usage activity without touching files or
redeploying. It's a single shared password, not per-user accounts: set `ADMIN_PASSWORD` in `backend/.env`
(leave unset to disable admin login) and log in at `/admin/login`.

| Page | What it does |
|---|---|
| `/admin` (Overview) | The same aggregate stats as `/api/dashboard/summary` and `/api/dashboard/messages` |
| `/admin/farmers` | Paginated list of anonymous farmer records (no phone numbers or other identity) |
| `/admin/crop-prices` | A rate/source/date grid for daily price updates |
| `/admin/content` | A raw JSON editor for `credit_info.json`, `certifications.json` and `knowledge_base.json` |

The `backend/app/data/*.json` files stay the single source of truth - an admin save writes the file directly and
clears the loader's cache (`app/services/content_service.py`), so the next chat turn sees the change immediately,
with no restart. `/api/dashboard/*` now requires the same admin login.

## 9. Later phases (not implemented)

Google Sheet crop rates and SARIMA/Prophet expected ranges (`CropRateProvider`),
RAG/LLM for Ask Anything (`KnowledgeService.search`), speech-to-text for voice notes, native-speaker review of the Urdu/Sindhi
translations, automated weekly updates, Looker Studio reporting, Alembic migrations, and Docker deployment.

> Weather is live from Open-Meteo (free for non-commercial use). All crop rates, credit, certification and knowledge-base content in `backend/app/data/` is **placeholder sample
> data** and must be replaced with the project team's verified content before any pilot.
