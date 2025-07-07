from fastapi import APIRouter
from app.api.endpoints import soil_data, users, analysis

api_router = APIRouter()

api_router.include_router(soil_data.router, prefix="/soil-data", tags=["soil-data"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])