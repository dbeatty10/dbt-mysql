# @TODO Remove these lines
from dbt.contracts.results import (
    TableMetadata, CatalogTable, CatalogResults, Primitive, CatalogKey,
    StatsItem, StatsDict, ColumnMetadata
)
import dbt.utils

from dbt.utils import lowercase
######################


from concurrent.futures import as_completed, Future
# from typing import List, Optional, Callable, Set
from typing import (
    Optional, Tuple, Callable, Iterable, Type, Dict, Any, List, Mapping,
    Iterator, Union, Set
)

import agate

from dbt.adapters.sql import SQLAdapter
from dbt.adapters.base import BaseRelation
# from dbt.adapters.base import BaseColumn
from dbt.adapters.base import Column as BaseColumn
from dbt.adapters.mysql import MySQLConnectionManager
from dbt.adapters.mysql import MySQLRelation
from dbt.adapters.mysql import MySQLColumn


from dbt.clients.agate_helper import table_from_rows

from dbt.clients.agate_helper import empty_table, merge_tables, table_from_rows
from dbt.contracts.graph.manifest import Manifest
from dbt.logger import GLOBAL_LOGGER as logger
# from dbt.utils import filter_null_values, executor
from dbt.utils import executor


from dbt.adapters.base.relation import InformationSchema


GET_CATALOG_MACRO_NAME = 'get_catalog'
LIST_RELATIONS_MACRO_NAME = 'list_relations_without_caching'


def _expect_row_value(key: str, row: agate.Row):
    if key not in row.keys():
        raise InternalException(
            'Got a row without "{}" column, columns: {}'
            .format(key, row.keys())
        )
    return row[key]


def _catalog_filter_schemas(manifest: Manifest) -> Callable[[agate.Row], bool]:
    """Return a function that takes a row and decides if the row should be
    included in the catalog output.

    In MySQL, Databases and schemas are the same thing.
    """

    # get_used_schemas:
    # frozenset({(None, 'dbt_test_201117231308844744382177')})
    # _catalog_filter_schemas schemas:
    # frozenset({'dbt_test_201117231308844744382177'})
    # test table_schema: dbt_test_201117231308844744382177
    # table_schema.lower(): dbt_test_201117231308844744382177
    # in schemas?: False


    print("get_used_schemas:")
    print(manifest.get_used_schemas())

    schemas = frozenset(s.lower()
                        for d, s in manifest.get_used_schemas())

    print("_catalog_filter_schemas schemas:")
    print(schemas)

    def test(row: agate.Row) -> bool:
        table_schema = _expect_row_value('table_schema', row)

        print(f"test table_schema: {table_schema}")
        print(f"table_schema.lower(): {table_schema.lower()}")
        print(f"in schemas?: {table_schema.lower() in schemas}")

        # the schema may be present but None, which is not an error and should
        # be filtered out
        if table_schema is None:
            return False

        # @TODO temporary for troubleshooting
        # return table_schema.lower() in schemas
        return True
    return test


class MySQLAdapter(SQLAdapter):
    Relation = MySQLRelation
    Column = MySQLColumn
    ConnectionManager = MySQLConnectionManager

    @classmethod
    def date_function(cls):
        return 'current_date()'

    @classmethod
    def convert_datetime_type(
            cls, agate_table: agate.Table, col_idx: int
    ) -> str:
        return "timestamp"

    def quote(self, identifier):
        return '`{}`'.format(identifier)

    def list_relations_without_caching(
        self, schema_relation: MySQLRelation
    ) -> List[MySQLRelation]:

        logger.info("Start list_relations_without_caching")
        kwargs = {'schema_relation': schema_relation}
        try:
            results = self.execute_macro(
                LIST_RELATIONS_MACRO_NAME,
                kwargs=kwargs
            )
        except dbt.exceptions.RuntimeException as e:
            errmsg = getattr(e, 'msg', '')
            if f"MySQL database '{schema_relation}' not found" in errmsg:
                return []
            else:
                description = "Error while retrieving information about"
                logger.debug(f"{description} {schema_relation}: {e.msg}")
                return []

        relations = []
        for row in results:
            if len(row) != 4:
                raise dbt.exceptions.RuntimeException(
                    f'Invalid value from "mysql__list_relations_without_caching ...", '
                    f'got {len(row)} values, expected 4'
                )
            _, name, _schema, information = row
            rel_type = information
            relation = self.Relation.create(
                schema=_schema,
                identifier=name,
                type=rel_type
            )
            logger.info(f"Adding relation {relation}")
            relations.append(relation)

        return relations

    def get_columns_in_relation(self, relation: Relation) -> List[MySQLColumn]:
        rows: List[agate.Row] = super().get_columns_in_relation(relation)
        return self.parse_show_columns(relation, rows)

    def parse_show_columns(
            self,
            relation: Relation,
            raw_rows: List[agate.Row]
    ) -> List[MySQLColumn]:

        for idx, column in enumerate(raw_rows):
            logger.info(f"parse_show_columns MySQLColumn: {column}")
            logger.info(f"parse_show_columns column: {column.column}")
            logger.info(f"parse_show_columns dtype: {column.dtype}")

        return [MySQLColumn(
            table_database=None,
            table_schema=relation.schema,
            table_name=relation.name,
            table_type=relation.type,
            table_owner=None,
            table_stats=None,
            column=column.column,
            column_index=idx,
            dtype=column.dtype,
        ) for idx, column in enumerate(raw_rows)]

    def get_relation(
        self, database: str, schema: str, identifier: str
    ) -> Optional[BaseRelation]:
        if not self.Relation.include_policy.database:
            database = None

        return super().get_relation(database, schema, identifier)

    def check_schema_exists(self, database: str, schema: str) -> bool:
        print("logger: start/end check_schema_exists()")
        return schema in self.list_schemas(database)

    @classmethod
    def _catalog_filter_table(
        cls, table: agate.Table, manifest: Manifest
    ) -> agate.Table:
        """Filter the table as appropriate for catalog entries. Subclasses can
        override this to change filtering rules on a per-adapter basis.
        """
        # force database + schema to be strings
        table = table_from_rows(
            table.rows,
            table.column_names,
            text_only_columns=['table_database', 'table_schema', 'table_name']
        )

        print("Unfiltered table:")
        # print(table)
        print(table.print_table())

        filtered_table = table.where(_catalog_filter_schemas(manifest))

        print("Filtered table:")
        # print(filtered_table)
        print(filtered_table.print_table())

        return filtered_table

    def _get_one_catalog(
        self,
        information_schema: InformationSchema,
        schemas: Set[str],
        manifest: Manifest,
    ) -> agate.Table:

        kwargs = {
            'information_schema': information_schema,
            'schemas': schemas
        }
        table = self.execute_macro(
            GET_CATALOG_MACRO_NAME,
            kwargs=kwargs,
            # pass in the full manifest so we get any local project
            # overrides
            manifest=manifest,
        )

        print("_get_one_catalog table:")
        # print(table)
        print(table.print_table())

        results = self._catalog_filter_table(table, manifest)

        # @TODO this is a hack just for troubleshooting
        # results = table

        print("_get_one_catalog results:")
        # print(results)
        print(results.print_table())

        return results

    # Methods used in adapter tests
    def update_column_sql(
        self,
        dst_name: str,
        dst_column: str,
        clause: str,
        where_clause: Optional[str] = None,
    ) -> str:
        print("update_column_sql")
        logger.info(f"update_column_sql({dst_name}, {dst_column}, {clause}, {where_clause})")
        logger.warn(f"update_column_sql({dst_name}, {dst_column}, {clause}, {where_clause})")
        logger.warning(f"update_column_sql({dst_name}, {dst_column}, {clause}, {where_clause})")

        clause = f'update {dst_name} set {dst_column} = {clause}'
        if where_clause is not None:
            clause += f' where {where_clause}'

        print(clause)
        logger.info(clause)
        logger.warn(clause)
        logger.warning(clause)
        return clause

    def timestamp_add_sql(
        self, add_to: str, number: int = 1, interval: str = 'hour'
    ) -> str:
        # for backwards compatibility, we're compelled to set some sort of
        # default. A lot of searching has lead me to believe that the
        # '+ interval' syntax used in postgres/redshift is relatively common
        # and might even be the SQL standard's intention.
        return f"date_add({add_to}, interval {number} {interval})"

    def string_add_sql(
        self, add_to: str, value: str, location='append',
    ) -> str:
        if location == 'append':
            return f"concat({add_to}, '{value}')"
        elif location == 'prepend':
            return f"concat({value}, '{add_to}')"
        else:
            raise RuntimeException(
                f'Got an unexpected location value of "{location}"'
            )

    def get_rows_different_sql(
        self,
        relation_a: MySQLRelation,
        relation_b: MySQLRelation,
        column_names: Optional[List[str]] = None,
    ) -> str:

        print("logger: start get_rows_different_sql()")

        # This method only really exists for test reasons
        names: List[str]
        if column_names is None:
            columns = self.get_columns_in_relation(relation_a)
            # names = sorted((self.quote(c.name) for c in columns))
            names = sorted((c.name for c in columns))
        else:
            # names = sorted((self.quote(n) for n in column_names))
            names = sorted((n for n in column_names))

        alias_a = "A"
        alias_b = "B"
        columns_csv_a = ', '.join([f"{alias_a}.{name}" for name in names])
        columns_csv_b = ', '.join([f"{alias_b}.{name}" for name in names])
        join_condition = ' AND '.join([f"{alias_a}.{name} = {alias_b}.{name}" for name in names])
        first_column = names[0]

        # MySQL doesn't have an EXCEPT or MINUS operator, so we need to simulate it
        COLUMNS_EQUAL_SQL = '''
        WITH
        a_except_b as (
            SELECT
                {columns_a}
            FROM {relation_a} as A
            LEFT OUTER JOIN {relation_b} as B
                ON {join_condition}
            WHERE B.{first_column} is null
        ),
        b_except_a as (
            SELECT
                {columns_b}
            FROM {relation_b} as B
            LEFT OUTER JOIN {relation_a} as A
                ON {join_condition}
            WHERE A.{first_column} is null
        ),
        diff_count as (
            SELECT
                1 as id,
                COUNT(*) as num_missing FROM (
                    SELECT * FROM a_except_b
                    UNION ALL
                    SELECT * FROM b_except_a
                ) as a
        ),
        table_a as (
            SELECT COUNT(*) as num_rows FROM {relation_a}
        ),
        table_b as (
            SELECT COUNT(*) as num_rows FROM {relation_b}
        ),
        row_count_diff as (
            SELECT
                1 as id,
                table_a.num_rows - table_b.num_rows as difference
            FROM table_a, table_b
        )
        SELECT
            row_count_diff.difference as row_count_difference,
            diff_count.num_missing as num_mismatched
        FROM row_count_diff
        INNER JOIN diff_count ON row_count_diff.id = diff_count.id
        '''.strip()

        sql = COLUMNS_EQUAL_SQL.format(
            # alias_a=alias_a,
            # alias_b=alias_b,
            first_column=first_column,
            columns_a=columns_csv_a,
            columns_b=columns_csv_b,
            join_condition=join_condition,
            relation_a=str(relation_a),
            relation_b=str(relation_b),
        )

        # logger.debug("Doug was HERE")
        # logger.info("Doug was here")
        # logger.warning("I'm warning you...")

        # @TODO
        # Temporality force a trivial query to help troubleshoot
        sql = "SELECT 0 as row_count_difference, 0 as num_mismatched FROM DUAL"

        print(sql)
        print("logger: end get_rows_different_sql()")

        return sql
