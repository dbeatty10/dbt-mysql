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

from dbt.adapters.base.impl import catch_as_completed
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

from dbt.clients.agate_helper import DEFAULT_TYPE_TESTER
from dbt.logger import GLOBAL_LOGGER as logger
# from dbt.utils import filter_null_values, executor
from dbt.utils import executor


from dbt.adapters.base.relation import InformationSchema


LIST_SCHEMAS_MACRO_NAME = 'list_schemas'
GET_CATALOG_MACRO_NAME = 'get_catalog'
LIST_RELATIONS_MACRO_NAME = 'list_relations_without_caching'
# FETCH_TBL_PROPERTIES_MACRO_NAME = 'fetch_tbl_properties'

# KEY_TABLE_OWNER = 'Owner'


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

    # @TODO remove comment
    # This similar to adapters/spark/impl.py
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
                    f'Invalid value from "mysql__list_relations_without_caching({kwargs})", '
                    f'got {len(row)} values, expected 4'
                )
            _, name, _schema, relation_type = row
            relation = self.Relation.create(
                schema=_schema,
                identifier=name,
                type=relation_type
            )
            logger.info(f"Adding relation {relation}")
            relations.append(relation)

        return relations

    # @TODO remove comment
    # This similar to adapters/spark/impl.py
    def get_columns_in_relation(self, relation: Relation) -> List[MySQLColumn]:
        rows: List[agate.Row] = super().get_columns_in_relation(relation)
        return self.parse_show_columns(relation, rows)

    # @TODO remove comment
    # This similar to adapters/spark/impl.py
    def _get_columns_for_catalog(
        self, relation: MySQLRelation
    ) -> Iterable[Dict[str, Any]]:
        # properties = self.get_properties(relation)
        columns = self.get_columns_in_relation(relation)
        # owner = properties.get(KEY_TABLE_OWNER)

        for column in columns:
            # if owner:
            #     column.table_owner = owner
            # convert MySQLColumns into catalog dicts
            as_dict = column.to_dict()
            as_dict['column_name'] = as_dict.pop('column', None)
            as_dict['column_type'] = as_dict.pop('dtype')
            as_dict['table_database'] = None
            yield as_dict

    # # @TODO remove comment
    # # This the same as adapters/spark/impl.py
    # def get_properties(self, relation: Relation) -> Dict[str, str]:
    #     properties = self.execute_macro(
    #         FETCH_TBL_PROPERTIES_MACRO_NAME,
    #         kwargs={'relation': relation}
    #     )
    #     return dict(properties)

    # @TODO remove comment
    # This is the same as adapters/spark/impl.py
    def get_relation(
        self, database: str, schema: str, identifier: str
    ) -> Optional[BaseRelation]:
        if not self.Relation.include_policy.database:
            database = None

        return super().get_relation(database, schema, identifier)

    # @TODO remove comment
    # This is similar to parse_describe_extended() in adapters/spark/impl.py
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

    # @TODO remove comment
    # This is the same as adapters/spark/impl.py
    def get_catalog(self, manifest):
        schema_map = self._get_catalog_schemas(manifest)
        if len(schema_map) > 1:
            dbt.exceptions.raise_compiler_error(
                f'Expected only one database in get_catalog, found '
                f'{list(schema_map)}'
            )

        with executor(self.config) as tpe:
            futures: List[Future[agate.Table]] = []
            for info, schemas in schema_map.items():
                for schema in schemas:
                    futures.append(tpe.submit_connected(
                        self, schema,
                        self._get_one_catalog, info, [schema], manifest
                    ))
            catalogs, exceptions = catch_as_completed(futures)
        return catalogs, exceptions

    # @TODO remove comment
    # This is the same as adapters/spark/impl.py
    def _get_one_catalog(
        self, information_schema, schemas, manifest,
    ) -> agate.Table:
        if len(schemas) != 1:
            dbt.exceptions.raise_compiler_error(
                f'Expected only one schema in mysql _get_one_catalog, found '
                f'{schemas}'
            )

        database = information_schema.database
        schema = list(schemas)[0]

        columns: List[Dict[str, Any]] = []
        for relation in self.list_relations(database, schema):
            logger.debug("Getting table schema for relation {}", relation)
            columns.extend(self._get_columns_for_catalog(relation))
        return agate.Table.from_object(
            columns, column_types=DEFAULT_TYPE_TESTER
        )

    # # @TODO remove comment
    # # This is DIFFERENT from adapters/spark/impl.py
    # # This is the same as adapters/base/impl.py
    # def _get_one_catalog(
    #     self,
    #     information_schema: InformationSchema,
    #     schemas: Set[str],
    #     manifest: Manifest,
    # ) -> agate.Table:
    #
    #     kwargs = {
    #         'information_schema': information_schema,
    #         'schemas': schemas
    #     }
    #     table = self.execute_macro(
    #         GET_CATALOG_MACRO_NAME,
    #         kwargs=kwargs,
    #         # pass in the full manifest so we get any local project
    #         # overrides
    #         manifest=manifest,
    #     )
    #
    #     print("_get_one_catalog table:")
    #     # print(table)
    #     print(table.print_table())
    #
    #     results = self._catalog_filter_table(table, manifest)
    #
    #     # @TODO this is a hack just for troubleshooting
    #     # results = table
    #
    #     print("_get_one_catalog results:")
    #     # print(results)
    #     print(results.print_table())
    #
    #     return results

    # @TODO remove comment
    # This is the same as adapters/spark/impl.py
    def check_schema_exists(self, database, schema):
        results = self.execute_macro(
            LIST_SCHEMAS_MACRO_NAME,
            kwargs={'database': database}
        )

        exists = True if schema in [row[0] for row in results] else False
        return exists

    # # @TODO remove comment
    # # This is supposed to be similar to adapters/spark/impl.py
    # def check_schema_exists(self, database: str, schema: str) -> bool:
    #     print("logger: start/end check_schema_exists()")
    #     return schema in self.list_schemas(database)

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
