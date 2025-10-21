from datetime import datetime
from sqlalchemy import (Column,
                       Integer,
                       String,
                       DateTime,
                       Index)
from sqlalchemy.orm import (Mapped,
                            mapped_column,
                            relationship)
from sqlalchemy.sql import func
from typing import List, TYPE_CHECKING

from app.models.calculation_model import Base

if TYPE_CHECKING:
    from app.models.calculation_result_model import CalculationResult


class Party(Base):
    """
    SQLAlchemy model for storing political parties/lists.
    """

    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Auto-incrementing primary key"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        doc="Unique name of the political party/list"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        doc="Timestamp when the party record was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        doc="Timestamp when the party record was last updated"
    )
    calculation_results: Mapped[List["CalculationResult"]] = relationship(
        "CalculationResult",
        back_populates="party",
        cascade="all, delete-orphan"
    )

    # Table-level constraints and indexes
    __table_args__ = (
        Index('idx_parties_name', 'name', unique=True),
        Index('idx_parties_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        """String representation of the Party model."""
        return f"<Party(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
