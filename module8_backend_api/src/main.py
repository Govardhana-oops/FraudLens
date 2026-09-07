"""FastAPI Main Application Entrypoint for AI-DIDSS Backend."""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_proto_root = str(Path(__file__).resolve().parent.parent.parent)
_mod_root = str(Path(__file__).resolve().parent.parent)

if _proto_root not in sys.path:
    sys.path.insert(0, _proto_root)
if _mod_root not in sys.path:
    sys.path.insert(0, _mod_root)

from .middleware.security_headers import SecurityHeadersMiddleware
from .routes import health, screening, watchlist, sync, audit

def create_app() -> FastAPI:
    """Creates and configures the FastAPI application instance."""
    app = FastAPI(
        title="AI-DIDSS Verification Decision Support API",
        version="1.0.0",
        description="High-Throughput Decision Support Backend API for Border Screening & Inspection Officers",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 1. Environment-Configurable CORS Middleware
    import os
    allowed_origins_env = os.environ.get("ALLOWED_ORIGINS")
    if allowed_origins_env:
        origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    else:
        # Default allowed origins for production judge URL and local dev
        origins = [
            "https://fraud-lens-7xjv.vercel.app",
            "https://fraud-lens-7xjy.vercel.app",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000"
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # 2. OWASP Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. Route Registration
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(screening.router, prefix="/api/v1")
    app.include_router(watchlist.router, prefix="/api/v1")
    app.include_router(sync.router, prefix="/api/v1")
    app.include_router(audit.router, prefix="/api/v1")

    # 4. Static Files Mount (Officer Console Web UI)
    new_frontend_dist = Path(_proto_root) / "fraudlens-new-frontend" / "dist"
    console_dir = new_frontend_dist if new_frontend_dist.exists() else (Path(_proto_root) / "module9_officer_console")
    if console_dir.exists():
        from fastapi.staticfiles import StaticFiles
        app.mount("/console", StaticFiles(directory=str(console_dir), html=True), name="console")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
