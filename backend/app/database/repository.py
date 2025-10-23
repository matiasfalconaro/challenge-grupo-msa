from typing import (List,
                    Dict,
                    Any,
                    Optional)
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import (select,
                        desc,
                        func)   

from app.models.calculation_model import Calculation
from app.models.party_model import Party
from app.models.calculation_result_model import CalculationResult
from app.models.voting_submission_model import VotingSubmission
from app.database.session import get_session_factory
from app.core.logging import get_logger

logger = get_logger(__name__)


def insert_calculation(total_seats: int, total_votes: int, results: List[Dict[str, Any]]) -> int:
    """
    Insert a calculation result into the database using normalized schema.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        # Validate inputs
        if total_seats <= 0:
            raise ValueError("total_seats must be positive")

        if total_votes < 0:
            raise ValueError("total_votes must be non-negative")

        if not isinstance(results, list):
            raise ValueError("results must be a list")

        # Step 1: Create the calculation record (metadata only)
        new_calculation = Calculation(
            total_seats=total_seats,
            total_votes=total_votes,
            timestamp=datetime.utcnow()
        )

        db.add(new_calculation)
        db.flush()  # Get the calculation ID without committing

        # Step 2: Process each party result
        for result in results:
            party_name = result.get('name')
            votes = result.get('votes', 0)
            seats = result.get('seats', 0)

            if not party_name:
                logger.warning("Skipping result with no party name")
                continue

            # Get party (must exist - no auto-creation)
            party = db.query(Party).filter(Party.name == party_name).first()
            if not party:
                raise ValueError(
                    f'Party "{party_name}" does not exist in the database. '
                    f'Only registered parties (Lista A-J) are allowed.'
                )

            # Create calculation result linking calculation to party
            calc_result = CalculationResult(
                calculation_id=new_calculation.id,
                party_id=party.id,
                votes=votes,
                seats=seats
            )
            db.add(calc_result)

        # Step 3: Commit all changes
        db.commit()
        db.refresh(new_calculation)

        record_id = new_calculation.id

        logger.info(
            f"Calculation saved with ID: {record_id} "
            f"({len(results)} parties, {total_seats} seats, {total_votes} votes)"
        )
        return record_id

    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        db.rollback()
        raise

    except Exception as e:
        logger.error(f"Failed to insert calculation: {e}", exc_info=True)
        db.rollback()
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()


def get_calculation_history(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve calculation history from the database using normalized schema.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        if limit <= 0:
            raise ValueError("limit must be positive")

        # Query calculations with eager loading of related data
        stmt = (
            select(Calculation)
            .order_by(desc(Calculation.timestamp))
            .limit(limit)
        )

        calculations = db.execute(stmt).scalars().all()

        result_list = []
        for calc in calculations:
            # Use the model's to_api_format method to get backward-compatible format
            # This method joins with calculation_results and parties automatically
            calc_dict = calc.to_api_format()
            calc_dict['id'] = calc.id  # Add id field for history display
            result_list.append(calc_dict)

        logger.info(f"Retrieved {len(result_list)} calculation records from normalized schema")
        return result_list

    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise

    except Exception as e:
        logger.error(f"Failed to retrieve calculation history: {e}", exc_info=True)
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()


def get_database_stats() -> Dict[str, Any]:
    """
    Get database statistics using SQLAlchemy ORM (normalized schema).
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        total_parties = db.query(func.count(Party.id)).scalar()
        total_calculations = db.query(func.count(Calculation.id)).scalar()
        total_results = db.query(func.count(CalculationResult.id)).scalar()
        most_recent_calc = (db.query(Calculation.timestamp).order_by(desc(Calculation.timestamp)).first())

        most_recent = most_recent_calc[0].isoformat() if most_recent_calc else None

        return {
            'total_calculations': total_calculations,
            'total_parties': total_parties,
            'total_results': total_results,
            'most_recent_calculation': most_recent,
            'schema_type': 'normalized (3 tables: parties, calculations, calculation_results)'
        }

    except Exception as e:
        logger.error(f"Failed to get database stats: {e}", exc_info=True)
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()


def get_calculation_by_id(calculation_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific calculation by ID using normalized schema.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()

        if calculation is None:
            return None

        # Use to_api_format to get backward-compatible format with results array
        result = calculation.to_api_format()
        result['id'] = calculation.id  # Add ID to result

        return result

    except Exception as e:
        logger.error(f"Failed to get calculation by ID: {e}", exc_info=True)
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()



def insert_voting_submissions(submissions: List[Dict[str, Any]]) -> List[int]:
    """
    Insert multiple voting submissions into the database.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        if not isinstance(submissions, list):
            raise ValueError("submissions must be a list")

        submission_ids = []

        for submission in submissions:
            party_name = submission.get('party_name')
            votes = submission.get('votes', 0)

            if not party_name:
                logger.warning("Skipping submission with no party name")
                continue

            if votes < 0:
                raise ValueError(f"Invalid votes for {party_name}: votes must be non-negative")

            # Get party (must exist - no auto-creation)
            party = db.query(Party).filter(Party.name == party_name).first()
            if not party:
                raise ValueError(
                    f'Party "{party_name}" does not exist in the database. '
                    f'Only registered parties (Lista A-J) are allowed.'
                )

            new_submission = VotingSubmission(
                party_id=party.id,
                votes=votes,
                submitted_at=datetime.utcnow()
            )

            db.add(new_submission)
            db.flush()  # Get the submission ID
            submission_ids.append(new_submission.id)

        db.commit()

        logger.info(f"Inserted {len(submission_ids)} voting submissions")
        return submission_ids

    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        db.rollback()
        raise

    except Exception as e:
        logger.error(f"Failed to insert voting submissions: {e}", exc_info=True)
        db.rollback()
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()


def get_all_voting_submissions(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all voting submissions from the database.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        query = db.query(VotingSubmission).order_by(desc(VotingSubmission.submitted_at))

        if limit is not None and limit > 0:
            query = query.limit(limit)

        submissions = query.all()

        result_list = [submission.to_dict() for submission in submissions]

        logger.info(f"Retrieved {len(result_list)} voting submissions")
        return result_list

    except Exception as e:
        logger.error(f"Failed to retrieve voting submissions: {e}", exc_info=True)
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()


def get_aggregated_votes() -> Dict[str, int]:
    """
    Aggregate all voting submissions by party name.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        # Use SQLAlchemy to join with Party and group by party name, sum votes
        aggregated = (
            db.query(
                Party.name,
                func.sum(VotingSubmission.votes).label('total_votes')
            )
            .join(VotingSubmission, VotingSubmission.party_id == Party.id)
            .group_by(Party.name)
            .all()
        )

        # Convert to dictionary
        result = {party_name: int(total_votes) for party_name, total_votes in aggregated}

        logger.info(f"Aggregated votes for {len(result)} parties from database")
        return result

    except Exception as e:
        logger.error(f"Failed to aggregate votes: {e}", exc_info=True)
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()


def get_voting_submissions_count() -> int:
    """
    Get total count of voting submissions.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        count = db.query(func.count(VotingSubmission.id)).scalar()
        return count

    except Exception as e:
        logger.error(f"Failed to count voting submissions: {e}", exc_info=True)
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()


def clear_all_voting_submissions() -> int:
    """
    Delete all voting submissions from the database.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()

    try:
        deleted_count = db.query(VotingSubmission).delete()
        db.commit()

        logger.info(f"Cleared {deleted_count} voting submissions")
        return deleted_count

    except Exception as e:
        logger.error(f"Failed to clear voting submissions: {e}", exc_info=True)
        db.rollback()
        raise ConnectionError(f"Database operation failed: {e}")

    finally:
        db.close()
