# FrameLens

> AI-powered digital asset protection for sports organizations — detects unauthorized usage of official media across platforms using a two-stage CLIP + pHash detection pipeline, Gemini AI risk analysis, and real-time YouTube cross-referencing.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://your-vercel-url.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Hugging%20Face%20Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/Ayushcodes123/framelens-backend)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

## Overview

FrameLens enables sports organizations to register their original media assets and automatically detect if that content appears — modified or unmodified — across other sources. A single scan cross-references the uploaded content against a protected Firestore dataset and live YouTube results simultaneously, then uses Google Gemini AI to assess the infringement risk and recommend an action.

---

## Live Deployment

| Service | Platform | URL |
|---|---|---|
| Frontend | Vercel | `https://your-vercel-url.vercel.app` |
| Backend API | Hugging Face Spaces (Docker) | `https://Ayushcodes123-framelens-backend.hf.space` |
| API Docs | FastAPI Swagger UI | `https://Ayushcodes123-framelens-backend.hf.space/docs` |

---

## Key Features

- **Two-stage detection** — pHash Hamming distance for fast candidate filtering, followed by CLIP ViT-B/32 cosine similarity for precise verification
- **Cross-platform scanning** — simultaneously checks your protected Firestore dataset and live YouTube results in a single API call
- **Gemini AI risk analysis** — determines modification type (cropped, trimmed, reposted, etc.), infringement risk level (High / Medium / Low), and a recommended action
- **Fallback analysis** — if Gemini is unavailable, risk is automatically derived from CLIP similarity score so scans never fail
- **Propagation graph** — interactive React Flow visualization showing how content has spread across sources
- **Dataset Manager** — register, view, and delete protected assets directly from the dashboard
- **Firebase Auth** — secure email/password authentication with protected routes

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.10, FastAPI, Uvicorn | API server |
| CLIP ViT-B/32 (Transformers + PyTorch) | Deep visual embeddings |
| imagehash + Pillow | Perceptual hashing (pHash) |
| OpenCV (headless) | Video frame extraction |
| Google Gemini 2.0 Flash | AI risk analysis |
| Firebase Admin SDK | Firestore database operations |
| YouTube Data API v3 | Cross-platform detection |

### Frontend
| Technology | Purpose |
|---|---|
| React 19, Vite | UI framework and build tool |
| React Router DOM | Client-side routing |
| Vanilla CSS | Custom Bold Typography design system |
| Firebase JS SDK | Authentication |
| React Flow (@xyflow/react) | Propagation graph visualization |
| Lucide React | Iconography |

### Infrastructure
| Service | Role |
|---|---|
| Hugging Face Spaces (Docker) | Backend hosting — 16GB RAM, free tier |
| Vercel | Frontend hosting — global CDN |
| Firebase Firestore | Protected asset dataset storage |
| Firebase Authentication | User authentication |
| cron-job.org | Keep-alive pings every 30 minutes |

---

## Detection Pipeline

```
User uploads image or video
        ↓
Stage 1 — pHash Hamming distance filter (threshold < 15)
        ↓ fast candidate narrowing
Stage 2 — CLIP cosine similarity verification
        ↓ (≥ 0.85 for dataset matches, ≥ 0.3 for YouTube)
Unified results from:
  ├── Firestore protected dataset
  └── YouTube Data API v3 (thumbnail comparison)
        ↓
Gemini AI analysis per match:
  ├── Modification type (cropped / trimmed / filtered / reposted / unknown)
  ├── Risk level (High / Medium / Low)
  └── Recommended action
        ↓
Results dashboard + Propagation graph
```

**Confidence Labels:**
- `HIGH CONFIDENCE` — similarity ≥ 85%
- `POSSIBLE MATCH` — similarity ≥ 50%
- `LOW SIMILARITY` — similarity < 50%

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/upload/image` | Upload and process an image |
| `POST` | `/upload/video` | Upload and process a video |
| `POST` | `/compare/unified` | Compare against dataset + YouTube (primary scan) |
| `POST` | `/compare/` | Compare against manual dataset only |
| `POST` | `/compare/auto` | Compare against Firestore dataset only |
| `POST` | `/youtube/compare` | Compare against YouTube only |
| `POST` | `/results/analyze` | Run Gemini AI risk analysis on matches |
| `POST` | `/dataset/add` | Register a new protected asset |
| `GET` | `/dataset/` | List all protected assets |
| `DELETE` | `/dataset/{id}` | Remove a protected asset |

Full interactive docs: `https://Ayushcodes123-framelens-backend.hf.space/docs`

---

## Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Firebase project with Firestore enabled
- Google Gemini API key
- YouTube Data API v3 key

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
API available at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App available at `http://localhost:5173`

### Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_CREDENTIALS=backend/firebase-credentials.json
YOUTUBE_API_KEY=your_youtube_api_key
```

Create a `.env` file inside the `frontend/` folder:

```env
VITE_API_BASE_URL=http://localhost:8000
```

> ⚠️ Never commit `firebase-credentials.json` or any `.env` files to version control.

---

## Application Pages

| Route | Page |
|---|---|
| `/` | Landing page |
| `/login` | Login / Sign Up |
| `/dashboard` | Upload content and start a scan |
| `/results` | Detection results + propagation graph |
| `/dataset` | Dataset Manager — register and manage protected assets |

---

## License

This project is licensed under the MIT License.
