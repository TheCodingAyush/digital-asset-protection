# FrameLens
AI-powered digital asset protection system that detects copyright infringement in videos and images across multiple sources.

## Current Status
- ✅ Backend API complete (9 endpoints)
- ✅ Firebase Firestore integration
- ✅ CLIP + pHash two-stage detection
- ✅ Gemini AI risk analysis
- ✅ Landing page
- ✅ Login/Signup (Firebase Auth)
- ✅ Upload page with scanning animation
- ✅ Results page with match cards
- ✅ YouTube API integration (in progress)
- ✅ Dataset Manager page (in progress)
- 🔄 Propagation graph (in progress)
- 🔄 Google Gemini Analysis(in progress)

## Tech Stack
- Backend: Python 3, FastAPI, CLIP ViT-B/32, pHash, Gemini AI, Firebase Firestore
- Frontend: React 19, Vite, Vanilla CSS, React Router
- AI: OpenAI CLIP, Google Gemini 2.0 Flash, perceptual hashing
- Database: Firebase Firestore

## System Flow
```
Upload video/image
      ↓
Extract frames + generate CLIP embeddings + pHash
      ↓
Compare against:
  ├── Local Firestore dataset
  ├── YouTube (thumbnails) [coming soon]
  └── Google Web Search [coming soon]
      ↓
Gemini AI risk analysis
      ↓
Results dashboard
```

## Getting Started

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
API docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

## Environment Variables
- `GEMINI_API_KEY=your_gemini_key`
- `FIREBASE_CREDENTIALS=firebase-credentials.json`

## Architecture
- Two-stage detection: pHash Hamming distance filter → CLIP cosine similarity verification
- Threshold: pHash distance < 15, CLIP similarity > 0.85
- Frame extraction: every 5 seconds for videos
- Dataset stored in Firebase Firestore
