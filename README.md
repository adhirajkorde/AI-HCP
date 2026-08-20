# AI-First HCP CRM Interaction Logger

An enterprise-grade, production-quality Healthcare Professional (HCP) CRM module focused on the **Log Interaction Screen** for pharmaceutical field representatives. Built using a modern React + Redux Toolkit frontend and a Python FastAPI backend powered by a LangGraph AI agent.

## Features

1. **Interactive Dashboard**: Real-time KPI summaries for total HCP profiles, total representative interactions, upcoming scheduled follow-up actions, and dynamic contact history timelines.
2. **Double-logging Interface**:
   - **Structured Form**: High-fidelity fields featuring responsive dropdowns, outcome inputs, calendar date selectors, and auto-populated medical specialties and clinics.
   - **Conversational AI Chat**: Field representatives type natural language logs (e.g., *"Met Dr Sharma today. Discussed CardioPlus. Interested in clinical trial data. Follow up next week"*). A LangGraph agent processes the text to extract entities, sentiment indices, and suggest follow-up schedules.
3. **HCP Directory**: List of doctor profiles with specialty categories, therapeutic alignments, and contact credentials.
4. **HCP Profile & Timeline**: Chronological, vertical flow timeline of all historical touches (meetings, calls, emails) combined with AI-generated doctor profiles.
5. **Follow-up Task Manager**: List of due dates sorted by priority with inline check-to-complete boxes syncing back to the database.
6. **Analytics and Charts**: Sentiment pie splits, engagement distributions, and pharmaceutical discussion share charts.

---

## Tech Stack

- **Frontend**: React + Redux Toolkit (state management) + Recharts (data visualizations) + Lucide React (icons)
- **Styling**: Vanilla CSS (highly tailored variables, gradients, glassmorphism, responsive grids)
- **Backend**: Python FastAPI (clean Service-Repository pattern) + SQLAlchemy ORM (compatible with PostgreSQL & SQLite)
- **AI Engine**: LangGraph + LangChain + Groq LLM `gemma2-9b-it` (also supports `llama-3.3-70b-versatile`)
- **Database**: PostgreSQL (with dynamic fallback to local SQLite `crm_fallback.db` for zero-dependency local testing)

---

## Architecture & Code Quality

The codebase utilizes professional enterprise design patterns:
- **Repository Pattern**: Abstracts database queries, isolating raw SQLAlchemy sessions from business services.
- **Service Layer**: Houses core business workflows, linking user authentication, automated follow-up scheduling, and dynamic sentiment calculations.
- **Double Fallback Agent Engine**: If no `GROQ_API_KEY` is provided, the backend falls back to an NLP text-matching heuristics parser. This ensures the conversational interface works offline immediately without breaking!
- **Password Safety**: Uses direct `bcrypt` hashing rounds (avoiding deprecated passlib conflicts) and pyjwt OAuth2 authorization standards.

---

## Directory Structure

```
AI/
├── crm_backend/            # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API Endpoints (auth, hcps, interactions, followups, analytics)
│   │   ├── core/           # Config settings, DB connector, Security utilities
│   │   ├── models/         # SQLAlchemy ORM schemas
│   │   ├── repositories/   # DB Repository pattern operations
│   │   ├── schemas/        # Pydantic validation models
│   │   ├── services/       # Core business workflows
│   │   └── agent/          # LangGraph agent definitions & tools
│   ├── requirements.txt    # Python packages
│   ├── seed.py             # Database seed population script
│   └── run.py              # Launcher script
└── frontend/               # React client SPA (Vite template)
    ├── src/
    │   ├── assets/
    │   ├── components/     # Reusable components (Sidebar, ToastContext, ProtectedRoute, Skeletons)
    │   ├── features/       # Redux slices (authSlice, hcpSlice, interactionSlice, followupSlice, analyticsSlice)
    │   ├── pages/          # Portal screens (Dashboard, LogInteraction, HCPList, HCPProfile, FollowUps, Analytics, Login)
    │   ├── services/       # Axios wrappers and request interceptors
    │   ├── store.js        # Redux store config
    │   ├── App.jsx         # App Router config
    │   └── main.jsx        # App root bootstrap
    └── package.json
```

---

## Getting Started

### 1. Backend Setup
1. Change directory to backend:
   ```bash
   cd crm_backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure settings:
   - Create a copy of `.env.example` as `.env`
   - By default, it will create and connect to a local SQLite database (`crm_fallback.db`).
   - To target a PostgreSQL database, edit `DATABASE_URL` in `.env`:
     ```env
     DATABASE_URL=postgresql://username:password@localhost:5432/db_name
     ```
   - To enable Groq LLM parsing, add your Groq API key:
     ```env
     GROQ_API_KEY=gsk_your_groq_api_key_here
     ```
4. Seed the database with default accounts and mock HCP records:
   ```bash
   python seed.py
   ```
5. Start the FastAPI server:
   ```bash
   python run.py
   ```
   The backend will be live on `http://localhost:8000`. You can inspect interactive Swagger documentation at `http://localhost:8000/docs`.

### 2. Frontend Setup
1. Change directory to frontend:
   ```bash
   cd ../frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be live at `http://localhost:5173/`.

### 3. Demo Portals Login
Use the pre-seeded credentials to explore the features:
- **Username**: `rep1` (or `admin`)
- **Password**: `password123`
- *(Or simply click the "Autofill Demo Representative" button on the login screen to sign in instantly.)*

---

## Deployment (AWS Free Tier)

Everything needed to deploy on a single free-tier EC2 instance is in the `deploy/` folder:

- **`deploy/setup.sh`** – one-click server setup (installs everything, builds, configures nginx + systemd)
- **`deploy/nginx.conf`** – serves the React build and proxies `/api` to the FastAPI backend
- **`deploy/ai-hcp.service`** – systemd service that keeps the backend running

Run it on the server (from inside the repo):

```bash
sudo bash deploy/setup.sh
```

The setup script also creates `crm_backend/.env` automatically (random JWT secret, SQLite database, optional `GROQ_API_KEY`).

## CI/CD (GitHub Actions)

A pipeline is included in `.github/workflows/deploy.yml`:

- **On every push/PR to `main`**: installs deps, smoke-tests the backend, lints + builds the frontend.
- **On push to `main`**: auto-deploys to your EC2 server via SSH.

To enable auto-deploy, add these secrets to your GitHub repo
(**Settings → Secrets and variables → Actions → New repository secret**):

| Secret | Value |
|--------|-------|
| `EC2_HOST` | Your server's public IP, e.g. `3.110.45.22` |
| `EC2_USER` | `ubuntu` |
| `EC2_KEY` | Full contents of your `ai-hcp-key.pem` file |

> The deploy step assumes the repo is already cloned at `~/ai-hcp` on the server (see Deployment section).
> After deploying once manually, every `git push` to `main` redeploys automatically.
