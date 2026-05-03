from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_backtest import router as backtest_router
from app.api.routes_report import router as report_router
from app.api.routes_screening import router as screening_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="AI-powered stock research workbench. Research only, not financial advice.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(screening_router, prefix="/api", tags=["screening"])
app.include_router(report_router, prefix="/api", tags=["report"])
app.include_router(backtest_router, prefix="/api", tags=["backtest"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
