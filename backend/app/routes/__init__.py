from fastapi import APIRouter
from .health import router as health_router
from .calculation import router as calculation_router
from .report import router as report_router


api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(calculation_router, tags=["Calculation"])
api_router.include_router(report_router, tags=["Reports"])

__all__ = ["api_router"]
