"""
VaaniSetu — FastAPI Application Entry Point
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.models.registry import registry
from backend.models.pool import init_pools
from backend.pipeline.queue import start_workers
from backend.routers import jobs, review, impact, glossary, health, auth
from backend.services.auth_service import seed_admin_user
from backend.utils.sse import bind_loop
from backend.utils.resources import preflight
from backend.config import HOST, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vaanisetu.main")

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("VaaniSetu starting up …")
    init_db()
    seed_admin_user()
    logger.info("Database and default admin initialised")

    # Let pipeline threads publish SSE onto this loop (see backend/utils/sse.py)
    loop = asyncio.get_running_loop()
    bind_loop(loop)

    # Tell the operator up front if this machine is too small, rather than
    # letting it discover that by swapping for ten minutes.
    fits, msg = preflight()
    (logger.info if fits else logger.warning)(msg)

    # Load models in a thread-pool executor to avoid blocking event loop
    await loop.run_in_executor(None, registry.load_all)

    # Build replica pools from whatever RAM is left once the models are in
    await loop.run_in_executor(None, init_pools)

    # Start the RAM-sized pool of job workers
    await start_workers()
    logger.info(f"Server ready at http://{HOST}:{PORT}")

    yield

    # Shutdown
    logger.info("VaaniSetu shutting down …")


app = FastAPI(
    title="VaaniSetu API",
    version="1.0.0",
    description="Offline AI Translation Platform for BAIF",
    lifespan=lifespan,
)

# CORS — allow LAN access from any device
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(review.router)
app.include_router(impact.router)
app.include_router(glossary.router)
app.include_router(health.router)

# Serve React build — must be after API routes
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
    logger.info(f"Serving frontend from {FRONTEND_DIST}")
else:
    logger.warning(f"Frontend dist not found at {FRONTEND_DIST} — run: npm run build")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)
