from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routers.analyze import router as analyze_router


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Resume Matcher API",
    description="AI-powered Resume and HR Requirement Matching System",
    version="1.0.0"
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    analyze_router
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="static"
)


@app.get(
    "/",
    include_in_schema=False
)
def frontend():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }