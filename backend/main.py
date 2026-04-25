from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import upload, compare, results, dataset, youtube

app = FastAPI(title="Digital Asset Protection System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(compare.router, prefix="/compare", tags=["compare"])
app.include_router(results.router, prefix="/results", tags=["results"])
app.include_router(dataset.router, prefix="/dataset", tags=["dataset"])
app.include_router(youtube.router, prefix="/youtube", tags=["youtube"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
