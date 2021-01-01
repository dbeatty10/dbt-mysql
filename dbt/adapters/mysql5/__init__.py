from dbt.adapters.mysql5.connections import MySQLConnectionManager
from dbt.adapters.mysql5.connections import MySQLCredentials
from dbt.adapters.mysql5.relation import MySQLRelation
from dbt.adapters.mysql5.column import MySQLColumn
from dbt.adapters.mysql5.impl import MySQLAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import mysql5


Plugin = AdapterPlugin(
    adapter=MySQLAdapter,
    credentials=MySQLCredentials,
    include_path=mysql5.PACKAGE_PATH)
