from typing import (Any,
                    Dict,
                    List,
                    TYPE_CHECKING)
from datetime import datetime
from sqlalchemy import (Column,
                       Integer,
                       DateTime,
                       CheckConstraint,
                       Index,)
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            relationship)
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from app.models.calculation_result_model import CalculationResult


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Calculation(Base):
    """
    SQLAlchemy model for storing D'Hondt calculation metadata.
    """

    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Auto-incrementing primary key"
    )
    total_seats: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Total number of seats to allocate - must be positive"
    )
    total_votes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Total number of votes - must be non-negative"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        doc="Timestamp when the calculation was performed"
    )
    calculation_results: Mapped[List["CalculationResult"]] = relationship(
        "CalculationResult",
        back_populates="calculation",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint('total_seats > 0', name='calculations_total_seats_check'),
        CheckConstraint('total_votes >= 0', name='calculations_total_votes_check'),
        Index('idx_calculations_timestamp', 'timestamp', postgresql_ops={'timestamp': 'DESC'}),
        Index('idx_calculations_total_seats', 'total_seats'),
    )

    def __repr__(self) -> str:
        """String representation of the Calculation model."""
        return (
            f"<Calculation(id={self.id}, "
            f"total_seats={self.total_seats}, "
            f"total_votes={self.total_votes}, "
            f"timestamp={self.timestamp})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        """
        return {
            'id': self.id,
            'total_seats': self.total_seats,
            'total_votes': self.total_votes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    def to_api_format(self) -> Dict[str, Any]:
        """
        Convert normalized database model to flat API response format.
        Returns a dictionary with calculation metadata and nested results array.
        """
        results = [
            result.to_api_format()
            for result in sorted(self.calculation_results, key=lambda x: x.seats, reverse=True)
        ]

        return {
            'total_seats': self.total_seats,
            'total_votes': self.total_votes,
            'results': results,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
