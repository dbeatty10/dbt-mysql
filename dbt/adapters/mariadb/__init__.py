from dbt.adapters.mariadb.connections import MariaDBConnectionManager  # noqa
from dbt.adapters.mariadb.connections import MariaDBCredentials
from dbt.adapters.mariadb.relation import MariaDBRelation  # noqa
from dbt.adapters.mariadb.column import MariaDBColumn  # noqa
from dbt.adapters.mariadb.impl import MariaDBAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import mariadb


Plugin = AdapterPlugin(
    adapter=MariaDBAdapter,  # type: ignore[arg-type]
    credentials=MariaDBCredentials,
    include_path=mariadb.PACKAGE_PATH,
)
