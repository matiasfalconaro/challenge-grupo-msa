from typing import (List,
                    Dict,
                    Any,
                    Optional,
                    Union)
from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import (SQLAlchemyError,
                            IntegrityError,
                            DataError,
                            OperationalError)

from app.database.session import get_session_factory
from app.core.logging import get_logger

logger = get_logger(__name__)


class RawQueryExecutor:
    """
    Secure executor for raw SQL queries with SQLAlchemy integration.
    """

    def __init__(self):
        """Initialize the RawQueryExecutor with session factory."""
        self.session_factory = get_session_factory()
        logger.debug("RawQueryExecutor initialized")

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error, rolling back: {e}", exc_info=True)
            raise
        finally:
            session.close()


    def execute_query(self,
                     sql: str,
                     params: Optional[Dict[str, Any]] = None,
                     session: Optional[Session] = None,
                     return_format: str = "dict") -> List[Dict[str, Any]] | List[tuple] | Any:
        """
        Execute a SELECT query and return results.
        """
        if not sql or not isinstance(sql, str):
            raise ValueError("SQL query must be a non-empty string")

        if params is not None and not isinstance(params, dict):
            raise ValueError("Parameters must be a dictionary")

        params = params or {}

        valid_formats = ["dict", "tuple", "scalar"]
        if return_format not in valid_formats:
            raise ValueError(f"return_format must be one of {valid_formats}")

        logger.info(f"Executing SELECT query: {sql[:100]}...")
        logger.debug(f"Query parameters: {params}")

        manage_session = session is None
        if manage_session:
            session = self.session_factory()

        try:
            result = session.execute(text(sql), params)

            if return_format == "scalar":
                value = result.scalar()
                logger.info(f"Query executed successfully, returned scalar: {value}")
                return value
            elif return_format == "tuple":
                rows = result.fetchall()
                logger.info(f"Query executed successfully, returned {len(rows)} rows")
                return rows
            else:
                columns = result.keys()
                rows = result.fetchall()

                result_dicts = [dict(zip(columns, row)) for row in rows]
                logger.info(f"Query executed successfully, returned {len(result_dicts)} rows")
                return result_dicts

        except DataError as e:
            logger.error(f"Data error in query execution: {e}", exc_info=True)
            raise ValueError(f"Invalid data in query: {e}")

        except OperationalError as e:
            logger.error(f"Operational error in query execution: {e}", exc_info=True)
            raise ConnectionError(f"Database connection error: {e}")

        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error in query execution: {e}", exc_info=True)
            raise RuntimeError(f"Database query failed: {e}")

        finally:
            if manage_session:
                session.close()


    def execute_update(self,
                       sql: str,
                       params: Optional[Dict[str, Any]] = None,
                       session: Optional[Session] = None,
                       auto_commit: bool = True) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        """
        if not sql or not isinstance(sql, str):
            raise ValueError("SQL query must be a non-empty string")

        if params is not None and not isinstance(params, dict):
            raise ValueError("Parameters must be a dictionary")

        params = params or {}

        logger.info(f"Executing UPDATE query: {sql[:100]}...")
        logger.debug(f"Query parameters: {params}")

        manage_session = session is None
        if manage_session:
            session = self.session_factory()

        try:
            result = session.execute(text(sql), params)
            affected_rows = result.rowcount

            if auto_commit and manage_session:
                session.commit()
                logger.info(f"Query executed and committed, {affected_rows} rows affected")
            else:
                logger.info(f"Query executed, {affected_rows} rows affected (not committed)")

            return affected_rows

        except IntegrityError as e:
            if manage_session:
                session.rollback()
            logger.error(f"Integrity constraint violation: {e}", exc_info=True)
            raise ValueError(f"Database constraint violation: {e}")

        except DataError as e:
            if manage_session:
                session.rollback()
            logger.error(f"Data error in query execution: {e}", exc_info=True)
            raise ValueError(f"Invalid data in query: {e}")

        except OperationalError as e:
            if manage_session:
                session.rollback()
            logger.error(f"Operational error in query execution: {e}", exc_info=True)
            raise ConnectionError(f"Database connection error: {e}")

        except SQLAlchemyError as e:
            if manage_session:
                session.rollback()
            logger.error(f"SQLAlchemy error in query execution: {e}", exc_info=True)
            raise RuntimeError(f"Database query failed: {e}")

        finally:
            if manage_session:
                session.close()


    def execute_many(self,
                    sql: str,
                    params_list: List[Dict[str, Any]],
                    session: Optional[Session] = None,
                    auto_commit: bool = True) -> int:
        """
        Execute the same query multiple times with different parameters.
        """
        if not sql or not isinstance(sql, str):
            raise ValueError("SQL query must be a non-empty string")

        if not isinstance(params_list, list) or not params_list:
            raise ValueError("params_list must be a non-empty list")

        for params in params_list:
            if not isinstance(params, dict):
                raise ValueError("Each item in params_list must be a dictionary")

        logger.info(f"Executing batch query with {len(params_list)} parameter sets")
        logger.debug(f"Query: {sql[:100]}...")

        manage_session = session is None
        if manage_session:
            session = self.session_factory()

        try:
            total_affected = 0

            for params in params_list:
                result = session.execute(text(sql), params)
                total_affected += result.rowcount

            if auto_commit and manage_session:
                session.commit()
                logger.info(
                    f"Batch query executed and committed, "
                    f"{total_affected} total rows affected"
                )
            else:
                logger.info(
                    f"Batch query executed, "
                    f"{total_affected} total rows affected (not committed)"
                )

            return total_affected

        except IntegrityError as e:
            if manage_session:
                session.rollback()
            logger.error(f"Integrity constraint violation in batch: {e}", exc_info=True)
            raise ValueError(f"Database constraint violation: {e}")

        except SQLAlchemyError as e:
            if manage_session:
                session.rollback()
            logger.error(f"SQLAlchemy error in batch execution: {e}", exc_info=True)
            raise RuntimeError(f"Batch query failed: {e}")

        finally:
            if manage_session:
                session.close()


    def execute_transaction(self,
                           operations: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute multiple queries in a single transaction.
        """
        if not isinstance(operations, list) or not operations:
            raise ValueError("operations must be a non-empty list")

        logger.info(f"Executing transaction with {len(operations)} operations")

        with self.get_session() as session:
            results = []

            for i, operation in enumerate(operations):
                if not isinstance(operation, dict):
                    raise ValueError(f"Operation {i} must be a dictionary")

                sql = operation.get('sql')
                params = operation.get('params', {})
                op_type = operation.get('type', 'update')

                if op_type == 'query':
                    result = self.execute_query(
                        sql=sql,
                        params=params,
                        session=session
                    )
                else:
                    result = self.execute_update(
                        sql=sql,
                        params=params,
                        session=session,
                        auto_commit=False
                    )

                results.append(result)
                logger.debug(f"Operation {i+1}/{len(operations)} completed")

            logger.info(f"Transaction completed successfully with {len(results)} results")
            return results
