# FrameLens 🛡️

**FrameLens** is an AI-powered digital asset protection system designed to detect copyright infringement in videos and images across multiple sources. Built specifically for sports organizations and media companies, it helps protect official media from unauthorized use and distribution.

## 🚀 Live Deployment

The system is fully deployed and accessible online:

- **Frontend (Vercel):** [https://digital-asset-protection.vercel.app](https://digital-asset-protection.vercel.app) *(Note: Replace with your actual Vercel URL if different)*
- **Backend (Hugging Face Spaces):** Hosted on HF Spaces using FastAPI and Docker.

---

## ✨ Key Features

- **Two-Stage AI Detection Engine:** Combines **pHash** (perceptual hashing) for rapid candidate filtering and **CLIP ViT-B/32** for highly accurate deep visual semantic matching.
- **Cross-Platform Scanning:** Simultaneously scans the local protected dataset and external platforms like YouTube in a single upload.
- **Gemini Risk Analysis:** Automatically analyzes detected matches using Google Gemini 2.0 to determine modification types (cropped, filtered, etc.), infringement risk levels (High/Medium/Low), and recommended actions.
- **Propagation Graph:** Visualizes how content has spread across platforms using an interactive React Flow node graph.
- **Dataset Manager:** A dedicated dashboard for organizations to securely register and manage their protected original media.

## 💻 Tech Stack

### Frontend
- **Framework:** React 19, Vite
- **Routing & State:** React Router DOM
- **UI/UX:** Custom Vanilla CSS (Bold Typography Design System), Lucide React Icons
- **Visualizations:** React Flow (`@xyflow/react`)
- **Deployment:** Vercel

### Backend
- **Framework:** Python 3.10+, FastAPI, Uvicorn
- **AI & ML:** HuggingFace Transformers (CLIP), PyTorch, OpenCV (headless), imagehash
- **Risk Analysis:** Google Gemini AI
- **Database & Auth:** Firebase Firestore, Firebase Admin SDK
- **Integrations:** YouTube Data API v3
- **Deployment:** Docker, Hugging Face Spaces

## 🔄 System Architecture

1. **Asset Registration:** Organizations register original content via the Dataset Manager.
2. **Feature Extraction:** FrameLens extracts CLIP embeddings and pHash fingerprints, storing them securely in Firebase Firestore.
3. **Infringement Scan:** Users upload suspected infringing content (images or videos).
4. **Unified Comparison:** The system compares the uploaded media against the local Firestore dataset and the YouTube API.
5. **AI Risk Analysis:** Matches are sent to Gemini AI to assess modification types and infringement risk.
6. **Results Dashboard:** The user is presented with confidence labels, source badges, and a propagation map of the content spread.

## 🛠️ Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- Firebase project with Firestore enabled
- Google Gemini API key
- YouTube Data API v3 key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   FIREBASE_CREDENTIALS=firebase-credentials.json
   YOUTUBE_API_KEY=your_youtube_api_key
   ENVIRONMENT=development
   ```
4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
   *API documentation will be available at `http://localhost:8000/docs`*

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables in `frontend/.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
   *The app will be available at `http://localhost:5173`*

> ⚠️ **Security Note:** Never commit `firebase-credentials.json` or `.env` files to version control.
