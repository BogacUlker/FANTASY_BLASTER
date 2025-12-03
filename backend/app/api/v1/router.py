"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, players, predictions, rankings, teams

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(players.router, prefix="/players", tags=["Players"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["Rankings"])
