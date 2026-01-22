from fastapi import APIRouter
from app.api.v1.routes import api_routes_router as api_router

api_routes_router: APIRouter = APIRouter()

api_routes_router.include_router(router=api_router, prefix='/v1')