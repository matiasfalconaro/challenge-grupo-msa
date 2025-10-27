from fastapi import (APIRouter,
                     Request)
from app.models.schemas import HealthResponse
from app.core.rate_limit import (limiter,
                                 get_rate_limit)

router = APIRouter()


@router.get('/health', response_model=HealthResponse)
@limiter.limit(get_rate_limit("health"))
def health_check(request: Request):
    """
    Endpoint de verificación de salud.
    """
    return {
        'status': 'healthy',
        'service': 'dhondt-backend'
    }
