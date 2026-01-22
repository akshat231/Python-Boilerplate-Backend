from fastapi import APIRouter
from app.api.v1.routes.health import api_health_router as health_router

api_routes_router: APIRouter = APIRouter()

api_routes_router.include_router(router=health_router)