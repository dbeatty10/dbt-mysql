from dbt.adapters.sql import SQLAdapter
from dbt.adapters.mysql import MySQLConnectionManager
from dbt.adapters.mysql import MySQLRelation


class MySQLAdapter(SQLAdapter):
    Relation = MySQLRelation
    ConnectionManager = MySQLConnectionManager

    @classmethod
    def date_function(cls):
        return 'current_date()'
