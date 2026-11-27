# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Farmer Assistant (KisanRahnuma) MVP: a chatbot for farmers in Sindh (weather, crop rates, credit, certifications, Ask Anything) in English, Urdu and Sindhi. `backend/` is FastAPI + SQLAlchemy 2 + PostgreSQL; `frontend/` is React 18 + Vite + TypeScript + Tailwind v4 (public website, web chat simulator, dev dashboard). WhatsApp Business Cloud API is planned (Phase 3) as a thin channel adapter; README section 7 has the plan.

## Commands

Development is on Windows/PowerShell. Local PostgreSQL 18 runs on **port 5433**, and `psql` is not on PATH (`C:\Program Files\PostgreSQL\18\bin\psql.exe`).

Backend (run from `backend/`, venv at `backend/.venv`):

```powershell
pip install -r requirements.txt
python -m app.database.init_db            # create tables (--reset drops and recreates them)
python -m app.database.seed               # 42 demo farmers for the dashboard (--reset wipes data first)
uvicorn app.main:app --reload --port 8000 # API docs at /docs
.\.venv\Scripts\python.exe -m pytest -q                                   # all tests
.\.venv\Scripts\python.exe -m pytest tests/test_conversation.py -q        # one file
.\.venv\Scripts\python.exe -m pytest -q -k "test_name"                    # one test
```

Tests use in-memory SQLite (`tests/conftest.py` sets `DATABASE_URL` and overrides `get_db`), so PostgreSQL is not needed for them. There are no Alembic migrations: schema changes go through `Base.metadata.create_all`, so changing an existing model's columns means running `init_db --reset` locally.

Frontend (run from `frontend/`):

```powershell
npm run dev        # http://localhost:5173
npm run typecheck  # tsc --noEmit
npm run build      # typecheck + vite build
```

There is no linter or frontend test suite. Config comes from `backend/.env` (`DATABASE_URL`, `IDENTITY_HASH_SECRET`, `CORS_ORIGINS`, see `app/core/config.py`) and `frontend/.env` (`VITE_API_BASE_URL`, `VITE_WHATSAPP_NUMBER`).

## Architecture

**The conversation engine does not depend on any channel.** A channel adapter (`app/channels/web.py` for the simulator, `app/channels/whatsapp.py` for Meta's Cloud API) converts raw input to `InboundMessage` and `OutboundMessage` back to its own format (`app/domain/messages.py`). `ConversationService.handle()` in `app/services/conversation_service.py` is the **only** place chatbot decisions are made. Keep channel-specific logic out of it.

- **State machine:** the state (`ConversationState` in `app/domain/states.py`) and a JSON `context` are stored in the `conversation_sessions` table, which expires after 30 minutes of inactivity. `_handlers` maps each state to an `_on_<state>` method. A handler returns `None` when it doesn't understand the input; `_dispatch` then falls back to answering the text from the knowledge base. Use `Turn.go(state, **context)` to change state.
- **Order of checks:** `handle()` first drops redelivered messages (`InboundMessage.message_id` already seen, stored as an HMAC hash in `processed_messages`) and quick double taps of the same option (`repeat_tap_seconds`); both get no reply. Then `_dispatch`: feedback option ids (`fb:y|n:<service>:<response_id>`, which reply with the main menu), then voice, then language switch, then onboarding (language, then district in `CHOOSE_DISTRICT`, then one combined consent question in `CONSENT`), then global `home`/`menu` commands, then the handler for the current state. To add a feature: add a state, a handler, a menu option and presenter output.
- **Every outbound WhatsApp message is billed** (1,000 free per number per month; inbound is free). A turn returns at most one message, which carries the next step's buttons. Don't add extra confirmation messages or extra steps. The farmer's `district` is remembered on `farmer_consents` so weather and crop rates skip the district question ("My district" in the menu changes it). Outbound counts per channel and month are in `outbound_message_counts` (`GET /api/dashboard/messages`). Farmers are assumed not to type, so every flow must work with buttons alone.
- **WhatsApp limits apply to every channel:** ≤3 options become buttons, ≤10 a list, labels ≤24 characters (button titles ≤20). Text of a message with options should stay ≤1,024 characters (`MAX_INTERACTIVE_TEXT`), or WhatsApp needs two messages. Text uses WhatsApp markup (`*bold*`, `_italic_`), and the web frontend renders it (`src/lib/format.tsx`).
- **Wording:** all user-facing bot text lives in `app/i18n/{en,ur,sd}.py`, accessed through `t(key, lang, **kwargs)`, and is built into messages in `app/services/presenters.py`. Never hard-code strings in the engine. `tests/test_i18n.py` requires the `ur`/`sd` catalogues to have exactly the same keys and `{placeholders}` as `en`, and every `{en, ur, sd}` object in the data files to be complete. When you add a key, add it to all three.
- **Feature services** (`weather_service`, `crop_service`, `credit_service`, `certification_service`, `knowledge_service`) return structured dataclasses from swappable providers (a `Protocol` plus a `Json*Provider` reading `app/data/*.json`). Weather is live: `OpenMeteoWeatherProvider` (no API key) fetches forecasts for the districts and coordinates in `app/data/weather.json`, caches them per district (`WEATHER_CACHE_MINUTES`), and on failure reuses today's cached forecast or returns none, so the engine replies `weather_unavailable`. WMO codes map to `cond_<code>` i18n keys. `WEATHER_PROVIDER=json` uses the sample forecasts; tests always do (`conftest.py`). Other real sources (Google Sheets, RAG) are meant to replace their providers the same way. Crop, credit, certification and knowledge data in `app/data/` is placeholder sample data.
- **WhatsApp webhook** (`app/api/whatsapp_webhook.py`): rejects requests without a valid `X-Hub-Signature-256` (`APP_SECRET`), runs the engine in a worker thread during the request, and sends replies to the Graph API in a `BackgroundTask` via `WhatsAppClient`. Tests override `get_settings` and `get_whatsapp_client` with a fake sender (`tests/test_whatsapp.py`). Settings accept the short `.env` names (`ACCESS_TOKEN`, `PHONE_NUMBER_ID`, `VERIFY_TOKEN`, `APP_SECRET`) or `WHATSAPP_*`.
- **Layers:** `api/` (routers) → `services/` → `repositories/` (all SQL lives here) → `models/`. `schemas/` holds the Pydantic request and response models.

## Privacy rules (requirements, enforced in code)

- Farmers are identified by a random UUID `farmer_id`. The channel identifier is stored only as an HMAC hash (`IDENTITY_HASH_SECRET`), never as a raw phone number. Channel message ids are hashed the same way, because WhatsApp ids encode the phone number.
- `usage_logs` rows are written **only** when `usage_consent` is true. Free-text questions are never stored, only the matched topic id.
- Feedback is always stored but is linked to the farmer only with consent. Withdrawing consent (`POST /api/consent`) deletes that farmer's usage logs and unlinks their feedback.

## Admin dashboard

`/admin` (password from `ADMIN_PASSWORD` in `backend/.env`, no per-user accounts) lets an operator edit chatbot
content and see farmer/usage activity. Login issues a stateless HMAC-signed token (`app/services/admin_auth.py`,
`require_admin` dependency on every `/api/admin/*` route and on `/api/dashboard/*`), not a server-side session.
Content stays in `backend/app/data/*.json` as the source of truth: `app/services/content_service.py` writes the
file and clears `data_loader.load_json`'s cache, so an edit applies on the very next request (`ConversationService`
builds fresh `CropService`/`CreditService`/etc. per request - see `app/api/chat.py`). Tests that write content use
the `isolated_content_dir` fixture (`tests/conftest.py`) so they never touch the real files on disk.

## Frontend notes

- Routes (`src/App.tsx`): the public site (`SiteLayout`: `/`, `/about`, `/services`, `/timeline`, `/team`, `/contact`), the farmer app (`AppShell`: `/chat`), and the admin area (`AdminShell`, gated by `src/lib/adminAuth.ts`: `/admin`, `/admin/farmers`, `/admin/crop-prices`, `/admin/content`; `/admin/login` is unguarded).
- Website copy (services, team, timeline, FAQ, contact) is in `src/content/site.ts`. The timeline phase status is computed from today's date.
- The chat flow is in `src/hooks/useChat.ts`, and API calls go through `src/api/client.ts` (types in `src/types/api.ts`). The anonymous `client_id` is kept in localStorage (`src/lib/storage.ts`).
- UI chrome strings are in `src/lib/i18n.ts` (Urdu and Sindhi are RTL). Bot message text comes from the backend.
- "Chat on WhatsApp" buttons open `wa.me/<VITE_WHATSAPP_NUMBER>?text=Hi`, or `/chat` when the number is unset (`src/lib/whatsapp.ts`).
