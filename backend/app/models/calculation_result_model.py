from sqlalchemy import (Column,
                       Integer,
                       ForeignKey,
                       CheckConstraint,
                       Index,
                       UniqueConstraint,)
from sqlalchemy.orm import (Mapped,
                            mapped_column,
                            relationship)
from typing import TYPE_CHECKING

from app.models.calculation_model import Base

if TYPE_CHECKING:
    from app.models.calculation_model import Calculation
    from app.models.party_model import Party


class CalculationResult(Base):
    """
    SQLAlchemy model for storing individual party results in calculations.
    """

    __tablename__ = "calculation_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Auto-incrementing primary key"
    )
    calculation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('calculations.id', ondelete='CASCADE'),
        nullable=False,
        doc="Foreign key referencing the calculation"
    )
    party_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('parties.id', ondelete='CASCADE'),
        nullable=False,
        doc="Foreign key referencing the party"
    )
    votes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Number of votes received by the party"
    )
    seats: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Number of seats allocated to the party"
    )
    calculation: Mapped["Calculation"] = relationship(
        "Calculation",
        back_populates="calculation_results"
    )
    party: Mapped["Party"] = relationship(
        "Party",
        back_populates="calculation_results"
    )

    # Table-level constraints and indexes
    __table_args__ = (
        CheckConstraint('votes >= 0', name='calculation_results_votes_check'),
        CheckConstraint('seats >= 0', name='calculation_results_seats_check'),
        UniqueConstraint('calculation_id', 'party_id', name='uq_calculation_party'),
        Index('idx_calculation_results_calculation_id', 'calculation_id'),
        Index('idx_calculation_results_party_id', 'party_id'),
        Index('idx_calculation_results_calc_party', 'calculation_id', 'party_id'),
        Index('idx_calculation_results_seats', 'seats'),
    )

    def __repr__(self) -> str:
        """String representation of the CalculationResult model."""
        return (
            f"<CalculationResult(id={self.id}, "
            f"calculation_id={self.calculation_id}, "
            f"party_id={self.party_id}, "
            f"votes={self.votes}, "
            f"seats={self.seats})>"
        )

    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.
        """
        return {
            'id': self.id,
            'calculation_id': self.calculation_id,
            'party_id': self.party_id,
            'votes': self.votes,
            'seats': self.seats,
            'party_name': self.party.name if self.party else None
        }

    def to_api_format(self) -> dict:
        """
        Convert normalized result to flat API format.
        Returns a simple dictionary with party name, votes, and seats.
        """
        return {
            'name': self.party.name if self.party else 'Unknown',
            'votes': self.votes,
            'seats': self.seats
        }
