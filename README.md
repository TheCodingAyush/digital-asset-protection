# FrameLens

AI-powered digital asset protection system that detects copyright infringement in videos and images.

## Tech Stack
- **Backend:** Python 3, FastAPI, CLIP (ViT-B/32), pHash, Gemini AI, Firebase Firestore
- **Frontend:** React 19, Vite, Vanilla CSS

## Features
- **Two-stage detection pipeline:** perceptual hash filtering + CLIP deep embeddings
- **Gemini AI risk analysis:** (modification type, risk level, recommendation)
- **Firebase Firestore:** dataset management
- **Full REST API:** with 9 endpoints

## Project Structure
```text
.
├── backend/                  # FastAPI python backend
│   ├── routers/              # API endpoint routes
│   ├── services/             # Core AI, hashing, and Firebase logic
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React 19 + Vite frontend
│   ├── src/                  
│   │   ├── App.jsx           
│   │   ├── LandingPage.jsx   # Brutalist landing page
│   │   ├── landing.css       # Core styling & design system
│   │   └── main.jsx          
│   ├── package.json          
│   └── vite.config.js        
├── .env.example              # Environment template
└── README.md
```

## Getting Started

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
Copy `.env.example` to `.env` and fill in:
- `GEMINI_API_KEY` — Google Gemini API key
- `FIREBASE_CREDENTIALS` — path to Firebase service account JSON

## Status
- ✅ Backend complete
- ✅ Landing page complete
- 🔄 Auth, Upload, Results pages — in progress
