from dbt.adapters.sql import SQLAdapter
from dbt.adapters.mysql import MySQLConnectionManager


class MySQLAdapter(SQLAdapter):
    ConnectionManager = MySQLConnectionManager
