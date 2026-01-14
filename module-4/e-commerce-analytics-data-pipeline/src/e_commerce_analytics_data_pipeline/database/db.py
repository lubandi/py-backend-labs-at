import os
import time
from contextlib import contextmanager

from dotenv import load_dotenv
from psycopg2 import DatabaseError, pool

load_dotenv()


class DatabaseManager:
    """
    A thread-safe PostgreSQL connection pool manager for efficient database operations.

    This class manages a pool of database connections using psycopg2's ThreadedConnectionPool,
    providing efficient connection reuse and automatic connection lifecycle management.

    Key Features:
    - Connection pooling for improved performance
    - Automatic retry mechanism for initial connection
    - Context managers for safe connection/cursor handling
    - Automatic transaction management (commit/rollback)
    - Environment-based configuration via .env file

    Attributes:
        _pool (ThreadedConnectionPool): The underlying PostgreSQL connection pool

    """

    def __init__(self):
        """
        Initialize the DatabaseManager and create a connection pool.

        The pool is lazily initialized on first use to handle cases where
        the database might not be immediately available.
        """
        self._pool = None
        self.initialize_pool()

    def initialize_pool(self):
        """
        Create and initialize the PostgreSQL connection pool with retry logic.

        This method:
        1. Attempts to create a ThreadedConnectionPool with configured parameters
        2. Retries up to 5 times with exponential backoff if connection fails
        3. Raises an exception if all retry attempts fail

        The pool maintains 1-20 connections, scaling based on demand.

        Raises:
            Exception: If connection cannot be established after all retries
        """
        if self._pool is not None:
            return

        retries = 5
        while retries > 0:
            try:
                self._pool = pool.ThreadedConnectionPool(
                    1,
                    20,
                    user=os.getenv("POSTGRES_USER", "admin"),
                    password=os.getenv("POSTGRES_PASSWORD", "password"),
                    host=os.getenv("POSTGRES_HOST", "localhost"),
                    port=os.getenv("POSTGRES_PORT", "5432"),
                    database=os.getenv("POSTGRES_DB", "ecommerce_db"),
                )
                print("Database connection pool created.")
                break
            except (Exception, DatabaseError) as error:
                print(f"Error connecting to DB: {error}. Retrying in 2s...")
                time.sleep(2)
                retries -= 1

        if self._pool is None:
            raise Exception("Could not connect to database after multiple retries.")

    @contextmanager
    def get_connection(self):
        """
        Context manager for acquiring and releasing a database connection.

        This method:
        1. Gets a connection from the pool
        2. Yields it for use within the context
        3. Returns the connection to the pool when context exits

        Yields:
            connection: A raw psycopg2 connection object from the pool

        Note:
            Connections are automatically returned to the pool even if
            exceptions occur within the context.

        """
        if self._pool is None:
            self.initialize_pool()

        assert self._pool is not None  # suppress Pylance warning about None check

        con = self._pool.getconn()
        try:
            yield con
        finally:
            self._pool.putconn(con)

    @contextmanager
    def get_cursor(self):
        """
        Context manager for database operations with automatic transaction handling.

        This is the recommended way to execute database queries as it provides:
        1. Automatic cursor creation and cleanup
        2. Transaction management (commit on success, rollback on exception)
        3. Connection pooling integration

        The context manager ensures ACID compliance:
        - **A**tomicity: All operations succeed or none do (via commit/rollback)
        - **C**onsistency: Database constraints are maintained
        - **I**solation: Transactions are isolated (depends on DB isolation level)
        - **D**urability: Committed changes persist

        Yields:
            cursor: A psycopg2 cursor object for executing SQL commands

        Raises:
            Exception: Any exception during cursor execution is raised after rollback

        """
        with self.get_connection() as con:
            cursor = con.cursor()
            try:
                yield cursor
                con.commit()  # Commit transaction if no exceptions
            except Exception as e:
                con.rollback()  # Rollback transaction on any exception
                raise e
            finally:
                cursor.close()

    def close(self):
        """
        Close all connections in the pool and clean up resources.

        This should be called when the application is shutting down to ensure
        all database connections are properly closed. Failing to call this
        method may result in connection leaks.

        """
        if self._pool:
            self._pool.closeall()
            print("PostgreSQL connection pool is closed")


# instance for application-wide use
db = DatabaseManager()
