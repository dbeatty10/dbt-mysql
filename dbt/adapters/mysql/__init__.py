from dbt.adapters.mysql.connections import MySQLConnectionManager  # noqa
from dbt.adapters.mysql.connections import MySQLCredentials
from dbt.adapters.mysql.relation import MySQLRelation  # noqa
from dbt.adapters.mysql.column import MySQLColumn  # noqa
from dbt.adapters.mysql.impl import MySQLAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import mysql


Plugin = AdapterPlugin(
    adapter=MySQLAdapter,  # type: ignore[arg-type]
    credentials=MySQLCredentials,
    include_path=mysql.PACKAGE_PATH,
)
