import pytest

from dbt.tests.adapter.constraints.test_constraints import (
    BaseTableConstraintsColumnsEqual,
    BaseViewConstraintsColumnsEqual,
    BaseTableContractSqlHeader,
    BaseIncrementalContractSqlHeader,
    BaseIncrementalConstraintsColumnsEqual,
    BaseConstraintsRuntimeDdlEnforcement,
    BaseConstraintsRollback,
    BaseIncrementalConstraintsRuntimeDdlEnforcement,
    BaseIncrementalConstraintsRollback,
    BaseModelConstraintsRuntimeEnforcement,
    BaseConstraintQuotedColumn,
)

from dbt.tests.adapter.constraints.fixtures import (
    my_incremental_model_sql,
    model_contract_header_schema_yml,
    model_schema_yml,
    my_model_wrong_order_depends_on_fk_sql,
    foreign_key_model_sql,
    my_model_with_quoted_column_name_sql,
    my_model_incremental_wrong_order_depends_on_fk_sql,
    model_fk_constraint_schema_yml,
)

from tests.functional.adapter.constraints.fixtures import (
    my_model_with_nulls_sql,
    my_model_incremental_with_nulls_sql,
    my_model_contract_sql_header_sql,
    my_model_incremental_contract_sql_header_sql,
    mariadb_model_schema_yml,
    mariadb_model_fk_constraint_schema_yml,
    constrained_model_schema_yml,
    model_quoted_column_schema_yml,
)


class MySQLColumnEqualSetup:
    @pytest.fixture
    def int_type(self):
        return "INTEGER"

    @pytest.fixture
    def schema_int_type(self):
        return "INTEGER"

    @pytest.fixture
    def data_types(self, int_type, schema_int_type, string_type):
        # sql_column_value, schema_data_type, error_data_type
        return [
            ["1", schema_int_type, int_type],
            ["'str'", string_type, string_type],
            ["cast('2019-01-01' as date)", "date", "DATE"],
            ["cast('2013-11-03 00:00:00' as datetime)", "datetime", "DATETIME"],
        ]


class TestMySQLTableConstraintsColumnsEqual(
    MySQLColumnEqualSetup, BaseTableConstraintsColumnsEqual
):
    pass


class TestMySQLViewConstraintsColumnsEqual(MySQLColumnEqualSetup, BaseViewConstraintsColumnsEqual):
    pass


class TestMySQLIncrementalConstraintsColumnsEqual(
    MySQLColumnEqualSetup, BaseIncrementalConstraintsColumnsEqual
):
    pass


class TestMySQLTableContractsSqlHeader(BaseTableContractSqlHeader):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_contract_sql_header.sql": my_model_contract_sql_header_sql,
            "constraints_schema.yml": model_contract_header_schema_yml,
        }


class TestMySQLIncrementalContractsSqlHeader(BaseIncrementalContractSqlHeader):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_contract_sql_header.sql": my_model_incremental_contract_sql_header_sql,
            "constraints_schema.yml": model_contract_header_schema_yml,
        }


# MySQL 5 does not support CHECK constraints
_expected_mysql5_ddl_enforcement_sql = """
    create table <model_identifier> (
        id integer not null primary key unique,
        color text,
        date_day text
    )
    (
        select id, color, date_day
        from (
            -- depends_on: <foreign_key_model_identifier>
            select
              'blue' as color,
              1 as id,
              '2019-01-01' as date_day
        ) as model_subq
    )
"""

# MariaDB does not support multiple column-level CHECK constraints
# Additionally, MariaDB requires CHECK constraints to come last
_expected_mariadb_ddl_enforcement_sql = """
    create table <model_identifier> (
        id integer not null primary key unique check (id > 0 AND id >= 1),
        color text,
        date_day text
    )
    (
        select id, color, date_day
        from (
            -- depends_on: <foreign_key_model_identifier>
            select
              'blue' as color,
              1 as id,
              '2019-01-01' as date_day
        ) as model_subq
    )
"""

_expected_mysql_ddl_enforcement_sql = """
    create table <model_identifier> (
        id integer not null primary key check ((id > 0)) check (id >= 1) unique,
        color text,
        date_day text
    )
    (
        select id, color, date_day
        from (
            -- depends_on: <foreign_key_model_identifier>
            select
              'blue' as color,
              1 as id,
              '2019-01-01' as date_day
        ) as model_subq
    )
"""


class TestMySQLTableConstraintsDdlEnforcement(BaseConstraintsRuntimeDdlEnforcement):
    @pytest.fixture(scope="class")
    def models(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mariadb":
            return {
                "my_model.sql": my_model_incremental_wrong_order_depends_on_fk_sql,
                "foreign_key_model.sql": foreign_key_model_sql,
                "constraints_schema.yml": mariadb_model_fk_constraint_schema_yml,
            }
        else:
            return {
                "my_model.sql": my_model_incremental_wrong_order_depends_on_fk_sql,
                "foreign_key_model.sql": foreign_key_model_sql,
                "constraints_schema.yml": model_fk_constraint_schema_yml,
            }

    @pytest.fixture(scope="class")
    def expected_sql(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mysql5":
            return _expected_mysql5_ddl_enforcement_sql
        elif dbt_profile_target["type"] == "mariadb":
            return _expected_mariadb_ddl_enforcement_sql
        else:
            return _expected_mysql_ddl_enforcement_sql


class TestMySQLIncrementalConstraintsDdlEnforcement(
    BaseIncrementalConstraintsRuntimeDdlEnforcement
):
    @pytest.fixture(scope="class")
    def models(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mariadb":
            return {
                "my_model.sql": my_model_incremental_wrong_order_depends_on_fk_sql,
                "foreign_key_model.sql": foreign_key_model_sql,
                "constraints_schema.yml": mariadb_model_fk_constraint_schema_yml,
            }
        else:
            return {
                "my_model.sql": my_model_incremental_wrong_order_depends_on_fk_sql,
                "foreign_key_model.sql": foreign_key_model_sql,
                "constraints_schema.yml": model_fk_constraint_schema_yml,
            }

    @pytest.fixture(scope="class")
    def expected_sql(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mysql5":
            return _expected_mysql5_ddl_enforcement_sql
        elif dbt_profile_target["type"] == "mariadb":
            return _expected_mariadb_ddl_enforcement_sql
        else:
            return _expected_mysql_ddl_enforcement_sql


class TestMySQLTableConstraintsRollback(BaseConstraintsRollback):
    @pytest.fixture(scope="class")
    def models(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mariadb":
            return {
                "my_model.sql": my_incremental_model_sql,
                "constraints_schema.yml": mariadb_model_schema_yml,
            }
        else:
            return {
                "my_model.sql": my_incremental_model_sql,
                "constraints_schema.yml": model_schema_yml,
            }

    @pytest.fixture(scope="class")
    def expected_error_messages(self):
        return ["Column 'id' cannot be null"]

    @pytest.fixture(scope="class")
    def null_model_sql(self):
        return my_model_with_nulls_sql


class TestMySQLIncrementalConstraintsRollback(BaseIncrementalConstraintsRollback):
    @pytest.fixture(scope="class")
    def models(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mariadb":
            return {
                "my_model.sql": my_incremental_model_sql,
                "constraints_schema.yml": mariadb_model_schema_yml,
            }
        else:
            return {
                "my_model.sql": my_incremental_model_sql,
                "constraints_schema.yml": model_schema_yml,
            }

    @pytest.fixture(scope="class")
    def expected_error_messages(self):
        return ["Column 'id' cannot be null"]

    @pytest.fixture(scope="class")
    def null_model_sql(self):
        return my_model_incremental_with_nulls_sql


# MySQL 5 does not support CHECK constraints
_expected_mysql5_runtime_enforcement_sql = """
    create table <model_identifier> (
        id integer not null,
        color text,
        date_day text,
        primary key (id),
        constraint strange_uniqueness_requirement unique (color(10), date_day(20))
    )
    (
        select id, color, date_day
        from (
            -- depends_on: <foreign_key_model_identifier>
            select
              'blue' as color,
              1 as id,
              '2019-01-01' as date_day
        ) as model_subq
    )
"""

_expected_mysql_runtime_enforcement_sql = """
    create table <model_identifier> (
        id integer not null,
        color text,
        date_day text,
        check ((id > 0)),
        check (id >= 1),
        primary key (id),
        constraint strange_uniqueness_requirement unique (color(10), date_day(20))
    )
    (
        select id, color, date_day
        from (
            -- depends_on: <foreign_key_model_identifier>
            select
              'blue' as color,
              1 as id,
              '2019-01-01' as date_day
        ) as model_subq
    )
"""


class TestMySQLModelConstraintsRuntimeEnforcement(BaseModelConstraintsRuntimeEnforcement):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_model_wrong_order_depends_on_fk_sql,
            "foreign_key_model.sql": foreign_key_model_sql,
            "constraints_schema.yml": constrained_model_schema_yml,
        }

    @pytest.fixture(scope="class")
    def expected_sql(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mysql5":
            return _expected_mysql5_runtime_enforcement_sql
        else:
            return _expected_mysql_runtime_enforcement_sql


# MySQL 5 does not support CHECK constraints
_expected_mysql5_quoted_column_sql = """
    create table <model_identifier> (
        id integer not null,
        `from` text not null,
        date_day text
    )
    (
        select id, `from`, date_day
        from (
            select
              'blue' as `from`,
              1 as id,
              '2019-01-01' as date_day
        ) as model_subq
    )
"""

_expected_mysql_quoted_column_sql = """
    create table <model_identifier> (
        id integer not null,
        `from` text not null,
        date_day text,
        check ((`from` = 'blue'))
    )
    (
        select id, `from`, date_day
        from (
            select
              'blue' as `from`,
              1 as id,
              '2019-01-01' as date_day
        ) as model_subq
    )
"""


class TestMySQLConstraintQuotedColumn(BaseConstraintQuotedColumn):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_model_with_quoted_column_name_sql,
            "constraints_schema.yml": model_quoted_column_schema_yml,
        }

    @pytest.fixture(scope="class")
    def expected_sql(self, dbt_profile_target):
        if dbt_profile_target["type"] == "mysql5":
            return _expected_mysql5_quoted_column_sql
        else:
            return _expected_mysql_quoted_column_sql
