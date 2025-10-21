from typing import Any, Dict, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (Column,
                       Integer,
                       String,
                       DateTime,
                       CheckConstraint,
                       Index,
                       ForeignKey,)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.calculation_model import Base

if TYPE_CHECKING:
    from app.models.party_model import Party


class VotingSubmission(Base):
    """
    SQLAlchemy model for storing individual voting data submissions.
    """

    __tablename__ = "voting_submissions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Auto-incrementing primary key"
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
        doc="Number of votes submitted for this party - must be non-negative"
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        doc="Timestamp when the voting data was submitted"
    )
    party: Mapped["Party"] = relationship(
        "Party",
        backref="voting_submissions"
    )


    __table_args__ = (
        CheckConstraint('votes >= 0', name='voting_submissions_votes_check'),
        Index('idx_voting_submissions_party_id', 'party_id'),
        Index('idx_voting_submissions_submitted_at', 'submitted_at', postgresql_ops={'submitted_at': 'DESC'}),
    )

    def __repr__(self) -> str:
        """String representation of the VotingSubmission model."""
        return (
            f"<VotingSubmission(id={self.id}, "
            f"party_id='{self.party_id}', "
            f"votes={self.votes}, "
            f"submitted_at={self.submitted_at})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        """
        return {
            'id': self.id,
            'party_id': self.party_id,
            'party_name': self.party.name if self.party else None,
            'votes': self.votes,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
