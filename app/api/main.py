from fastapi import FastAPI
from app.api.routes import router
import os

# =========================
# APP INITIALIZATION
# =========================

app = FastAPI(
    title="SHL Assessment Recommendation API",
    description=(
        "Conversational AI system for "
        "SHL assessment recommendations "
        "using hybrid RAG architecture."
    ),
    version="1.0.0"
)

# =========================
# ROOT ENDPOINT
# =========================

@app.get("/")
def root():
    return {
        "message": "SHL Assessment Recommendation API is running."
    }

# =========================
# HEALTH ENDPOINT
# =========================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

# =========================
# CHAT ROUTES
# =========================

app.include_router(router)

# =========================
# HF / PRODUCTION ENTRYPOINT
# =========================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 7860))

    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )