from typing import List
from fastapi import (APIRouter,
                     HTTPException,
                     Request,
                     status)
from backend.app.models.schemas import (VotingSubmissionRequest,
                               VotingSubmissionResponse,
                               VotingSubmissionItem,
                               AggregatedVotesResponse,
                               CalculateAggregateRequest,
                               CalculationResponse,
                               ClearSubmissionsResponse,
                               CalculationHistoryItem)
from app.services import DhondtService
from app.core.rate_limit import (limiter,
                                 get_rate_limit)

router = APIRouter()


@router.post('/submit-votes', response_model=VotingSubmissionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit("calculate"))
def submit_votes(request: Request, submission: VotingSubmissionRequest):
    """
    Envía datos de votación para almacenarlos en la base de datos.
    """
    try:
        result = DhondtService.submit_votes(submission)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


@router.get('/voting-submissions', response_model=List[VotingSubmissionItem])
@limiter.limit(get_rate_limit("history"))
def get_voting_submissions(request: Request, limit: int = 100):
    """
    Obtiene todas las sumisiones de votos almacenadas.
    """
    try:
        submissions = DhondtService.get_voting_submissions(limit=limit)
        return submissions
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to retrieve submissions: {str(e)}')


@router.get('/aggregated-votes', response_model=AggregatedVotesResponse)
@limiter.limit(get_rate_limit("calculate"))
def get_aggregated_votes(request: Request):
    """
    Obtiene los votos agregados de todas las sumisiones sin calcular escaños.
    """
    try:
        aggregated = DhondtService.get_aggregated_votes()
        return aggregated
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to aggregate votes: {str(e)}')


@router.post('/calculate-aggregate', response_model=CalculationResponse, status_code=status.HTTP_200_OK)
@limiter.limit(get_rate_limit("calculate"))
def calculate_aggregate(request: Request, calc_request: CalculateAggregateRequest):
    """
    Calcula la asignación de escaños D'Hondt usando TODOS los datos agregados de la base de datos.
    """
    try:
        result = DhondtService.calculate_aggregate(calc_request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')


@router.delete('/clear-submissions', response_model=ClearSubmissionsResponse, status_code=status.HTTP_200_OK)
@limiter.limit(get_rate_limit("save"))
def clear_submissions(request: Request):
    """
    Elimina todas las sumisiones de votos de la base de datos.
    """
    try:
        result = DhondtService.clear_submissions()
        return result
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to clear submissions: {str(e)}')


@router.get('/calculation-history', response_model=List[CalculationHistoryItem])
@limiter.limit(get_rate_limit("history"))
def get_calculation_history(request: Request, limit: int = 20):
    """
    Obtiene el historial de cálculos D'Hondt realizados.
    """
    try:
        history = DhondtService.get_calculation_history(limit=limit)
        return history
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to retrieve calculation history: {str(e)}')
