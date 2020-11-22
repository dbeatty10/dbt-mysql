from dbt.adapters.mysql.connections import MySQLConnectionManager
from dbt.adapters.mysql.connections import MySQLCredentials
from dbt.adapters.mysql.relation import MySQLRelation
from dbt.adapters.mysql.column import MySQLColumn
from dbt.adapters.mysql.impl import MySQLAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import mysql


Plugin = AdapterPlugin(
    adapter=MySQLAdapter,
    credentials=MySQLCredentials,
    include_path=mysql.PACKAGE_PATH)
