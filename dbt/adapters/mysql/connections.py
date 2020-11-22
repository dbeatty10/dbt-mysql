import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any
from typing import Optional
from typing import Tuple

import dbt.exceptions
import pyodbc
from dbt.adapters.sql import SQLConnectionManager
from dbt.contracts.connection import Connection
from dbt.contracts.connection import ConnectionState
from dbt.contracts.connection import Credentials
from dbt.logger import GLOBAL_LOGGER as logger


@dataclass
class MySQLCredentials(Credentials):
    driver: str
    server: str
    database: Optional[str]
    schema: str
    username: Optional[str]
    password: Optional[str]
    charset: Optional[str]

    _ALIASES = {
        "UID": "username",
        "user": "username",
        "PWD": "password",
        "host": "server",
    }

    def __post_init__(self):
        # mysql classifies database and schema as the same thing
        if (
            self.database is not None and
            self.database != self.schema
        ):
            raise dbt.exceptions.RuntimeException(
                f"    schema: {self.schema} \n"
                f"    database: {self.database} \n"
                f"On MySQL, database must be omitted or have the same value as"
                f" schema."
            )
        self.database = None

    @property
    def type(self):
        return "mysql"

    def connection_string(self, mask: bool = False):
        parts = []
        parts.append(f"DRIVER={{{self.driver}}}")
        parts.append(f"SERVER={self.server}")
        parts.append(f"UID={self.username}")
        if mask:
            parts.append("PWD=*********")
        else:
            parts.append(f"PWD={self.password}")

        if self.charset:
            parts.append(f"charset={self.charset}")

        return ";".join(parts)

    def _connection_keys(self):
        """
        Returns an iterator of keys to pretty-print in 'dbt debug'
        """
        return (
            "server",
            "database",
            "schema",
            "user",
        )


class MySQLConnectionManager(SQLConnectionManager):
    TYPE = "mysql"

    @classmethod
    def open(cls, connection: Connection):
        if connection.state == ConnectionState.OPEN:
            logger.debug("Connection is already open, skipping open.")
            return connection

        try:
            connection.handle = pyodbc.connect(
                connection.credentials.connection_string(), autocommit=True,
            )

            # MySQL tends to use a single encoding and does not differentiate
            # between "SQL_CHAR" and "SQL_WCHAR". Therefore when using its ODBC
            # drivers we must configure the connection to encode Unicode data
            # as UTF-8 and to decode both C buffer types using UTF-8.
            # See: https://github.com/mkleehammer/pyodbc/wiki/Unicode#mysql-and-postgresql
            connection.handle.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
            connection.handle.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
            connection.handle.setencoding(encoding='utf-8')

            connection.state = ConnectionState.OPEN
        except pyodbc.OperationalError as e:
            logger.debug(
                f"Got an error when attempting to open an odbc connection: '{e}'"
            )

            connection.handle = None
            connection.state = ConnectionState.FAIL

            raise dbt.exceptions.FailedToConnectException(str(e)) from e

        return connection

    def cancel(self, connection: Connection):
        connection.handle.close()

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        connection = self.get_thread_connection()
        if auto_begin and connection.transaction_open is False:
            self.begin()

        logger.debug(f'Using {self.TYPE} connection "{connection.name}".')

        with self.exception_handler(sql):
            if abridge_sql_log:
                log_sql = "{}...".format(sql[:512])
            else:
                log_sql = sql

            logger.debug(
                "On {connection_name}: {sql}",
                connection_name=connection.name,
                sql=log_sql,
            )
            pre = time.time()

            cursor = connection.handle.cursor()

            # PyODBC returns an error if bindings are passed in and there
            # aren't any parameter markers in the query.
            # We can get rid of this override when this issue is fixed:
            # https://github.com/fishtown-analytics/dbt/issues/1627
            if bindings is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, bindings)

            logger.debug(
                "SQL status: {status} in {elapsed:0.2f} seconds",
                status=self.get_status(cursor),
                elapsed=(time.time() - pre),
            )

            return connection, cursor

    @contextmanager
    def exception_handler(self, sql: str):
        try:
            yield
        except pyodbc.OperationalError as e:
            logger.debug(f"pyodbc OperationalError: {e}")

            try:
                self.release()
            except pyodbc.Error as e:
                logger.debug(f"Failed to release connection! {e}")

            raise dbt.exceptions.DatabaseException from e
        except Exception as e:
            logger.debug(f"Error running SQL: {sql}")
            logger.debug("Rolling back transaction.")
            self.release()
            if isinstance(e, dbt.exceptions.RuntimeException):
                # during a sql query, an internal to dbt exception was raised.
                # this sounds a lot like a signal handler and probably has
                # useful information, so raise it without modification.
                raise
            raise dbt.exceptions.RuntimeException(str(e)) from e

    @classmethod
    def get_status(cls, cursor):
        # There's no real way to get this from pyodbc, so just return "OK"
        return "OK"

    # pyodbc automatically handles transactions with the cursor
    def add_begin_query(self):
        pass

    def add_commit_query(self):
        pass
