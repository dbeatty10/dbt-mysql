from contextlib import contextmanager

import mysql.connector

import dbt.exceptions
from dbt.adapters.sql import SQLConnectionManager
from dbt.contracts.connection import AdapterResponse
from dbt.contracts.connection import Connection
from dbt.contracts.connection import Credentials
from dbt.logger import GLOBAL_LOGGER as logger
from dataclasses import dataclass
from typing import Optional


@dataclass
class MySQLCredentials(Credentials):
    server: str
    port: Optional[int]
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
        return "mysql5"

    def _connection_keys(self):
        """
        Returns an iterator of keys to pretty-print in 'dbt debug'
        """
        return (
            "server",
            "port",
            "database",
            "schema",
            "user",
        )


class MySQLConnectionManager(SQLConnectionManager):
    TYPE = "mysql5"

    @classmethod
    def open(cls, connection):
        if connection.state == 'open':
            logger.debug('Connection is already open, skipping open.')
            return connection

        credentials = cls.get_credentials(connection.credentials)
        kwargs = {}

        kwargs["host"] = credentials.server
        kwargs["user"] = credentials.username
        kwargs["passwd"] = credentials.password

        if credentials.port:
            kwargs["port"] = credentials.port

        try:
            connection.handle = mysql.connector.connect(**kwargs)
            connection.state = 'open'
        except mysql.connector.Error as e:
            logger.debug("Got an error when attempting to open a mysql 5.x"
                         "connection: '{}'"
                         .format(e))

            connection.handle = None
            connection.state = 'fail'

            raise dbt.exceptions.FailedToConnectException(str(e))

        return connection

    @classmethod
    def get_credentials(cls, credentials):
        return credentials

    def cancel(self, connection: Connection):
        connection.handle.close()

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except mysql.connector.DatabaseError as e:
            logger.debug('MySQL error: {}'.format(str(e)))

            try:
                self.rollback_if_open()
            except mysql.connector.Error:
                logger.debug("Failed to release connection!")
                pass

            raise dbt.exceptions.DatabaseException(str(e).strip()) from e

        except Exception as e:
            logger.debug("Error running SQL: {}", sql)
            logger.debug("Rolling back transaction.")
            self.rollback_if_open()
            if isinstance(e, dbt.exceptions.RuntimeException):
                # during a sql query, an internal to dbt exception was raised.
                # this sounds a lot like a signal handler and probably has
                # useful information, so raise it without modification.
                raise

            raise dbt.exceptions.RuntimeException(e) from e

    @classmethod
    def get_status(cls, cursor):
        # There's no real way to get this from mysql-connector-python, so just return "OK"
        return "OK"

    @classmethod
    def get_response(cls, cursor) -> AdapterResponse:
        code = "Unknown cursor state/status"

        return AdapterResponse(
            _message="{} {}".format(code, cursor.rowcount),
            rows_affected=cursor.rowcount,
            code=code
        )
