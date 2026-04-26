# FrameLens
AI-powered digital asset protection system that detects copyright infringement in videos and images across multiple sources — built for sports organizations to protect their official media.

## Project Status
- ✅ Backend API complete (11 endpoints)
- ✅ Firebase Firestore integration
- ✅ CLIP + pHash two-stage detection engine
- ✅ Gemini AI risk analysis
- ✅ YouTube Data API v3 integration
- ✅ Unified multi-source compare endpoint
- ✅ Landing page (Bold Typography design system)
- ✅ Login/Signup (Firebase Auth — Email/Password)
- ✅ Upload page with scanning animation
- ✅ Results page with confidence labels + source badges
- ✅ Propagation graph (React Flow)
- ✅ Dataset Manager (register + manage protected assets)

## Tech Stack

### Backend
- Python 3.12, FastAPI, Uvicorn
- OpenCV — video frame extraction
- CLIP ViT-B/32 (HuggingFace Transformers + PyTorch) — deep visual embeddings
- imagehash + Pillow — perceptual hashing
- Google Gemini 2.0 Flash — AI risk analysis
- Firebase Admin SDK — Firestore operations
- YouTube Data API v3 — cross-platform detection

### Frontend
- React 19, Vite
- React Router DOM — client-side routing
- Vanilla CSS — custom Bold Typography design system
- Firebase JS SDK — authentication
- React Flow (@xyflow/react) — propagation graph
- Lucide React + React Icons — iconography

### Database & Auth
- Firebase Firestore — protected asset dataset
- Firebase Authentication — Email/Password

## System Flow
Organization registers original content (Dataset Manager)
↓
FrameLens extracts CLIP embeddings + pHash fingerprints
↓
Stores in Firebase Firestore
↓
User uploads suspected infringing content
↓
Unified compare runs against:
├── Local Firestore dataset (CLIP + pHash)
└── YouTube API (thumbnail comparison)
↓
Gemini AI analyzes matches:
├── Modification type (cropped/trimmed/filtered/reposted)
├── Risk level (high/medium/low)
└── Recommended action
↓
Results dashboard + Propagation graph

## Detection Pipeline
- **Stage 1**: pHash Hamming distance filter (threshold < 15) — fast candidate narrowing
- **Stage 2**: CLIP cosine similarity verification (threshold > 0.85 for dataset, > 0.3 for YouTube)
- **Confidence Labels**: HIGH CONFIDENCE (≥85%) / POSSIBLE MATCH (≥50%) / LOW SIMILARITY (<50%)
- **Frame extraction**: every 5 seconds for videos

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload/video` | Upload and process video |
| POST | `/upload/image` | Upload and process image |
| POST | `/compare/` | Compare against manual dataset |
| POST | `/compare/auto` | Compare against Firestore dataset |
| POST | `/compare/unified` | Compare against dataset + YouTube |
| POST | `/youtube/compare` | Compare against YouTube only |
| POST | `/results/analyze` | Gemini risk analysis |
| POST | `/dataset/add` | Add asset to protected dataset |
| GET | `/dataset/` | Get all protected assets |
| DELETE | `/dataset/{id}` | Delete protected asset |

## Getting Started

### Prerequisites
- Python 3.12+
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
API docs available at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App available at `http://localhost:5173`

## Environment Variables
Create a `.env` file in the `backend/` folder:
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_CREDENTIALS=firebase-credentials.json
YOUTUBE_API_KEY=your_youtube_api_key
ENVIRONMENT=development
PORT=8000

> ⚠️ Never commit `firebase-credentials.json` or `.env` to version control.

## Pages
- `/` — Landing page
- `/login` — Login / Sign Up
- `/dashboard` — Upload & scan content
- `/results` — Detection results + propagation graph
- `/dataset` — Dataset manager (register protected assets)

## Key Features
- **Two-stage AI detection**: pHash for speed + CLIP for accuracy
- **Cross-platform scanning**: local dataset + YouTube in one scan
- **Propagation graph**: visual map of content spread
- **Gemini risk analysis**: automated infringement assessment
- **Confidence scoring**: HIGH CONFIDENCE / POSSIBLE MATCH / LOW SIMILARITY
- **Source badges**: clearly shows where each match was found
