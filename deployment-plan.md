# 🚀 ZomatoAI Deployment Plan

> **Backend → Railway** | **Frontend → Vercel**

---

## 📌 Architecture Overview

This project is currently a **Streamlit monolith** (UI + logic in one). To deploy backend on Railway and frontend on Vercel, we need to **split the app** into:

| Layer | Tech | Platform | Purpose |
|---|---|---|---|
| **Backend API** | FastAPI (Python) | Railway | Runs recommendation logic, calls Groq LLM, serves JSON |
| **Frontend** | Next.js / React | Vercel | Renders the ZomatoAI UI, calls the backend API |

```
┌─────────────────────┐        HTTPS/JSON        ┌─────────────────────┐
│   Vercel (Frontend) │  ───────────────────────► │  Railway (Backend)  │
│   Next.js / React   │ ◄───────────────────────  │  FastAPI (Python)   │
└─────────────────────┘                           └─────────────────────┘
                                                           │
                                                           ▼
                                                  ┌────────────────────┐
                                                  │  Hugging Face API  │
                                                  │  + Groq LLM API    │
                                                  └────────────────────┘
```

---

## Phase 1 — Refactor: Extract FastAPI Backend

### 1.1 Install FastAPI dependencies

Add these to `requirements.txt`:

```
fastapi>=0.111.0,<1.0.0
uvicorn[standard]>=0.29.0,<1.0.0
```

### 1.2 Create `api/main.py` (new FastAPI entrypoint)

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.user_input import UserPreferences
from app.data.repository import RestaurantRepository
from app.services.recommendation_service import RecommendationService

app = FastAPI(title="ZomatoAI API", version="1.0.0")

# Allow Vercel frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

repo = RestaurantRepository()
service = RecommendationService(repo)

@app.get("/health")
def health():
    return {"status": "ok", "groq": service.groq_client is not None}

@app.get("/locations")
def get_locations():
    return {"locations": repo.get_locations()}

@app.get("/stats")
def get_stats():
    return repo.get_stats()

@app.post("/recommend")
def recommend(prefs: UserPreferences):
    result = service.recommend(prefs)
    return result
```

### 1.3 Create `Procfile` (for Railway)

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### 1.4 Create `railway.toml`

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
```

---

## Phase 2 — Build: Next.js Frontend

### 2.1 Scaffold the frontend

Run from the project root:

```powershell
npx -y create-next-app@latest frontend --typescript --eslint --tailwind --app --no-src-dir --import-alias "@/*"
```

### 2.2 Key frontend files to create

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout (Outfit font, dark theme)
│   ├── page.tsx            # Main ZomatoAI page
│   └── globals.css         # Global dark theme CSS
├── components/
│   ├── Navbar.tsx          # Fixed navbar with Groq status badge
│   ├── PreferencesPanel.tsx  # Left preferences form
│   ├── RestaurantCard.tsx  # Glassmorphic restaurant card
│   ├── AIBanner.tsx        # AI summary banner
│   └── EmptyState.tsx      # Empty/loading states
├── lib/
│   └── api.ts              # API client (calls Railway backend)
└── .env.local              # NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

### 2.3 API client (`lib/api.ts`)

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export async function getLocations(): Promise<string[]> {
  const res = await fetch(`${API_URL}/locations`);
  const data = await res.json();
  return data.locations;
}

export async function getStats() {
  const res = await fetch(`${API_URL}/stats`);
  return res.json();
}

export async function getRecommendations(prefs: Preferences) {
  const res = await fetch(`${API_URL}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prefs),
  });
  return res.json();
}
```

---

## Phase 3 — Deploy Backend on Railway

### Step-by-step

1. **Push code to GitHub** — make sure `api/`, `app/`, `requirements.txt`, `Procfile`, `railway.toml` are committed.

2. **Create Railway project**
   - Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
   - Select your `zomato-milestone-1` repository

3. **Set environment variables** in Railway dashboard:

   | Variable | Value |
   |---|---|
   | `GROQ_API_KEY` | Your Groq API key from [console.groq.com](https://console.groq.com/keys) |
   | `GROQ_MODEL` | `llama-3.3-70b-versatile` |
   | `GROQ_TEMPERATURE` | `0.3` |
   | `GROQ_MAX_TOKENS` | `1024` |
   | `HF_DATASET_NAME` | `ManikaSaini/zomato-restaurant-recommendation` |
   | `MAX_CANDIDATES` | `50` |
   | `DEFAULT_TOP_N` | `5` |
   | `BUDGET_LOW_MAX` | `500` |
   | `BUDGET_MEDIUM_MAX` | `1500` |
   | `PORT` | *(Railway sets this automatically — do not set manually)* |

4. **Get your Railway URL** — Railway will generate a URL like `https://zomatoai-production-xxxx.railway.app`

5. **Test the backend:**
   ```
   GET https://your-app.railway.app/health
   GET https://your-app.railway.app/locations
   POST https://your-app.railway.app/recommend
   ```

> **⚠️ Cold Start Note:** Railway free tier services may sleep after inactivity. The first request after sleep loads the Hugging Face dataset (~few seconds). Consider upgrading to paid tier for production to avoid this.

---

## Phase 4 — Deploy Frontend on Vercel

### Step-by-step

1. **Push `frontend/` folder to GitHub** (same repo or separate).

2. **Go to [vercel.com](https://vercel.com)** → **New Project** → Import from GitHub.

3. **Configure the project:**
   - **Root Directory:** `frontend`
   - **Framework:** Next.js (auto-detected)
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

4. **Set environment variables** in Vercel dashboard:

   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://your-app.railway.app` *(your Railway URL)* |

5. **Update CORS in backend** — Once Vercel gives you a URL (e.g., `https://zomatoai.vercel.app`), update `api/main.py`:
   ```python
   allow_origins=["https://zomatoai.vercel.app"]
   ```
   Redeploy backend on Railway.

6. **Deploy** — Vercel auto-deploys on every push to `main`.

---

## Phase 5 — Files to Create / Modify

| File | Action | Notes |
|---|---|---|
| `api/__init__.py` | **CREATE** | Empty init file |
| `api/main.py` | **CREATE** | FastAPI app entrypoint |
| `Procfile` | **CREATE** | Railway start command |
| `railway.toml` | **CREATE** | Railway config |
| `requirements.txt` | **MODIFY** | Add `fastapi`, `uvicorn` |
| `frontend/` | **CREATE** | Entire Next.js app directory |
| `frontend/.env.local` | **CREATE** | `NEXT_PUBLIC_API_URL` (not committed) |
| `.gitignore` | **MODIFY** | Add `frontend/.env.local` |

---

## Environment Variables Summary

### Backend (Railway)
```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.3
GROQ_MAX_TOKENS=1024
HF_DATASET_NAME=ManikaSaini/zomato-restaurant-recommendation
MAX_CANDIDATES=50
DEFAULT_TOP_N=5
BUDGET_LOW_MAX=500
BUDGET_MEDIUM_MAX=1500
```

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

---

## Deployment Checklist

- [ ] Add `fastapi` and `uvicorn` to `requirements.txt`
- [ ] Create `api/__init__.py`
- [ ] Create `api/main.py` with CORS configured
- [ ] Create `Procfile`
- [ ] Create `railway.toml`
- [ ] Scaffold Next.js `frontend/` app
- [ ] Build `lib/api.ts` (API client)
- [ ] Port all Streamlit UI components to React/Next.js
- [ ] Commit everything to GitHub
- [ ] Deploy backend to Railway & note the URL
- [ ] Set all Railway environment variables
- [ ] Test Railway `/health` endpoint
- [ ] Update CORS `allow_origins` with Vercel URL
- [ ] Deploy frontend to Vercel
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel env vars
- [ ] Test end-to-end on production URLs
- [ ] Enable Railway health checks

---

## Cost Estimate

| Platform | Free Tier | Paid |
|---|---|---|
| **Railway** | $5 credit/month (Trial), then ~$5–10/mo (Hobby) | Scales with usage |
| **Vercel** | Free (Hobby) — unlimited frontend deploys | Pro: $20/mo |

> **Tip:** Both platforms have generous free tiers. For a portfolio/demo project, you can run this for free or near-free.

---

## Quick Reference URLs

- Railway Dashboard: https://railway.app/dashboard
- Vercel Dashboard: https://vercel.com/dashboard
- Groq API Keys: https://console.groq.com/keys
- Hugging Face Dataset: https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
