import re

from typing import ClassVar, List, Optional
from pydantic import (BaseModel,
                      Field,
                      field_validator)


class ListInput(BaseModel):
    """Input model for a political list with votes."""

    VALID_PARTIES: ClassVar[List[str]] = [
        'Lista A',
        'Lista B',
        'Lista C',
        'Lista D',
        'Lista E',
        'Lista F',
        'Lista G',
        'Lista H',
        'Lista I',
        'Lista J'
    ]

    name: str = Field(..., min_length=1, description="Nombre de la lista/partido político")
    votes: int = Field(..., ge=0, description="Número de votos recibidos")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """
        Validate that the party name is one of the predefined registered parties.
        """
        name = v.strip()

        if not name:
            raise ValueError('El nombre no puede estar vacío')

        if name not in cls.VALID_PARTIES:
            raise ValueError(
                f'Partido no válido: "{name}". Debe ser uno de los partidos registrados: {", ".join(cls.VALID_PARTIES)}'
            )

        return name


class ListResult(BaseModel):
    """Result model for a political list with allocated seats."""

    name: str
    votes: int
    seats: int


class CalculationResponse(BaseModel):
    """Response model for D'Hondt calculation."""

    total_seats: int
    total_votes: int
    results: List[ListResult]
    calculation_id: Optional[str] = Field(default=None, description="ID del cálculo guardado en la base de datos")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    service: str


class VotingSubmissionRequest(BaseModel):
    """Request model for submitting voting data."""

    lists: List[ListInput] = Field(..., min_length=1, description="Lista de votos por partido")


class VotingSubmissionResponse(BaseModel):
    """Response model for voting submission."""

    message: str
    submission_ids: List[int]
    total_submissions: int


class VotingSubmissionItem(BaseModel):
    """Model for a voting submission record."""

    id: int
    party_id: int
    party_name: str
    votes: int
    submitted_at: str


class AggregatedVotesResponse(BaseModel):
    """Response model showing aggregated votes before calculation."""

    total_submissions: int
    aggregated_parties: List[ListResult]
    total_votes: int


class CalculateAggregateRequest(BaseModel):
    """Request model for calculating D'Hondt on aggregate data."""

    total_seats: int = Field(..., gt=0, description="Número total de escaños a asignar")
    save_result: bool = Field(default=True, description="Guardar resultado en la base de datos")


class ClearSubmissionsResponse(BaseModel):
    """Response model for clearing submissions."""

    message: str
    deleted_count: int


class CalculationHistoryItem(BaseModel):
    """Model for a calculation history record."""

    id: int
    timestamp: str
    total_seats: int
    total_votes: int
    results: List[ListResult]
