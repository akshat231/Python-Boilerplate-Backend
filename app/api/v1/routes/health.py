from fastapi import APIRouter
from pydantic import BaseModel
from app.services.health import ping_port

api_health_router: APIRouter = APIRouter()

class HealthModel(BaseModel):
    port: int
    host: str

@api_health_router.post(path='/health')
def get_health(health_data: HealthModel) -> dict[str,str]:
    data: bool = ping_port(port=health_data.port, host=health_data.host)
    if data:
        return {'health': 'okay'}
    return {'health': 'Not Okay'}