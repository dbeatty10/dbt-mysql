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


#----------------------------------------------
# @TODO Remove this stuff when done troubleshooting

def get_stripped_prefix(source: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """Go through source, extracting every key/value pair where the key starts
    with the given prefix.
    """
    cut = len(prefix)
    return {
        k[cut:]: v for k, v in source.items()
        if k.startswith(prefix)
    }


PrimitiveDict = Dict[str, Primitive]


def build_catalog_table(data) -> CatalogTable:
    # build the new table's metadata + stats
    metadata = TableMetadata.from_dict(get_stripped_prefix(data, 'table_'))
    stats = format_stats(get_stripped_prefix(data, 'stats:'))

    return CatalogTable(
        metadata=metadata,
        stats=stats,
        columns={},
    )


# keys are database name, schema name, table name
class Catalog(Dict[CatalogKey, CatalogTable]):
    def __init__(self, columns: List[PrimitiveDict]):
        super().__init__()
        for col in columns:
            self.add_column(col)

    def get_table(self, data: PrimitiveDict) -> CatalogTable:
        database = data.get('table_database')
        if database is None:
            dkey: Optional[str] = None
        else:
            dkey = str(database)

        try:
            key = CatalogKey(
                dkey,
                str(data['table_schema']),
                str(data['table_name']),
            )
        except KeyError as exc:
            raise dbt.exceptions.CompilationException(
                'Catalog information missing required key {} (got {})'
                .format(exc, data)
            )
        table: CatalogTable
        if key in self:
            table = self[key]
        else:
            table = build_catalog_table(data)
            self[key] = table
        return table

    def add_column(self, data: PrimitiveDict):
        table = self.get_table(data)
        column_data = get_stripped_prefix(data, 'column_')
        # the index should really never be that big so it's ok to end up
        # serializing this to JSON (2^53 is the max safe value there)
        column_data['index'] = int(column_data['index'])

        column = ColumnMetadata.from_dict(column_data)
        table.columns[column.name] = column

    def make_unique_id_map(
        self, manifest: Manifest
    ) -> Tuple[Dict[str, CatalogTable], Dict[str, CatalogTable]]:
        nodes: Dict[str, CatalogTable] = {}
        sources: Dict[str, CatalogTable] = {}

        node_map, source_map = get_unique_id_mapping(manifest)
        table: CatalogTable
        for table in self.values():
            key = table.key()
            if key in node_map:
                unique_id = node_map[key]
                nodes[unique_id] = table.replace(unique_id=unique_id)

            unique_ids = source_map.get(table.key(), set())
            for unique_id in unique_ids:
                if unique_id in sources:
                    dbt.exceptions.raise_ambiguous_catalog_match(
                        unique_id,
                        sources[unique_id].to_dict(),
                        table.to_dict(),
                    )
                else:
                    sources[unique_id] = table.replace(unique_id=unique_id)
        return nodes, sources


def format_stats(stats: PrimitiveDict) -> StatsDict:
    """Given a dictionary following this layout:
        {
            'encoded:label': 'Encoded',
            'encoded:value': 'Yes',
            'encoded:description': 'Indicates if the column is encoded',
            'encoded:include': True,
            'size:label': 'Size',
            'size:value': 128,
            'size:description': 'Size of the table in MB',
            'size:include': True,
        }
    format_stats will convert the dict into a StatsDict with keys of 'encoded'
    and 'size'.
    """
    stats_collector: StatsDict = {}

    base_keys = {k.split(':')[0] for k in stats}
    for key in base_keys:
        dct: PrimitiveDict = {'id': key}
        for subkey in ('label', 'value', 'description', 'include'):
            dct[subkey] = stats['{}:{}'.format(key, subkey)]

        try:
            stats_item = StatsItem.from_dict(dct)
        except ValidationError:
            continue
        if stats_item.include:
            stats_collector[key] = stats_item

    # we always have a 'has_stats' field, it's never included
    has_stats = StatsItem(
        id='has_stats',
        label='Has Stats?',
        value=len(stats_collector) > 0,
        description='Indicates whether there are statistics for this table',
        include=False,
    )
    stats_collector['has_stats'] = has_stats
    return stats_collector

#----------------------------------------------


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

    # def list_schemas(self, database: str) -> List[str]:
    #     """
    #     Schemas in MySQL are called databases
    #     """
    #     results = self.connections.execute("show databases", fetch=True)
    #
    #     schemas = [row[0] for row in results]
    #
    #     return schemas

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
            # rel_type = ('view' if 'Type: VIEW' in information else 'table')
            rel_type = information
            relation = self.Relation.create(
                schema=_schema,
                identifier=name,
                type=rel_type
            )
            logger.info(f"Adding relation {relation}")
            relations.append(relation)

        return relations

    from dbt.adapters.base.meta import available
    @available.parse_list
    def get_missing_columns(
        self, from_relation: BaseRelation, to_relation: BaseRelation
    ) -> List[BaseColumn]:
        """Returns a list of Columns in from_relation that are missing from
        to_relation.
        """
        logger.info(f"Start get_missing_columns({from_relation}, {to_relation})")
        if not isinstance(from_relation, self.Relation):
            invalid_type_error(
                method_name='get_missing_columns',
                arg_name='from_relation',
                got_value=from_relation,
                expected_type=self.Relation)

        if not isinstance(to_relation, self.Relation):
            invalid_type_error(
                method_name='get_missing_columns',
                arg_name='to_relation',
                got_value=to_relation,
                expected_type=self.Relation)

        from_columns = {
            col.name: col for col in
            self.get_columns_in_relation(from_relation)
        }

        to_columns = {
            col.name: col for col in
            self.get_columns_in_relation(to_relation)
        }

        # (from_columns, to_columns) = (
        #    {},
        #    {'id': <MySQLColumn id (int)>, 'name': <MySQLColumn name (character varying(256))>, 'some_date': <MySQLColumn some_date (timestamp)>, 'dbt_scd_id': <MySQLColumn dbt_scd_id (character varying(32))>, 'dbt_updated_at': <MySQLColumn dbt_updated_at (timestamp)>, 'dbt_valid_from': <MySQLColumn dbt_valid_from (timestamp)>, 'dbt_valid_to': <MySQLColumn dbt_valid_to (character varying(19))>}
        # )
        logger.info(f"get_missing_columns: (from_columns, to_columns) = ({from_columns}, {to_columns})")

        missing_columns = set(from_columns.keys()) - set(to_columns.keys())

        return [
            col for (col_name, col) in from_columns.items()
            if col_name in missing_columns
        ]

    # def get_relation(
    #     self, database: str, schema: str, identifier: str
    # ) -> Optional[BaseRelation]:
    #     if not self.Relation.include_policy.database:
    #         database = None
    #
    #     return super().get_relation(database, schema, identifier)

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
            # column=column['Field'],
            column=column.column,
            column_index=idx,
            # dtype=column['Type'],
            dtype=column.dtype,
        ) for idx, column in enumerate(raw_rows)]

    def list_relations(
        self, database: Optional[str], schema: str
    ) -> List[BaseRelation]:

        import difflib

        logger.info("Start list_relations")
        if self._schema_is_cached(database, schema):
            logger.info("_schema_is_cached")
            logger.info(f"self.cache.get_relations({database}, {schema}) = {self.cache.get_relations(database, schema)}")
            logger.info(f"self.cache.relations.values() = {[(r.database, r.schema) for r in self.cache.relations.values()]}")

            for r in self.cache.relations.values():
                logger.info(f"Compare {lowercase(r.schema)} to {schema}")
                logger.info(lowercase(r.schema) == schema)
                # logger.info(difflib.ndiff(lowercase(r.schema), schema))

                # for i,s in enumerate(difflib.ndiff(lowercase(r.schema), schema)):
                #     if s[0]==' ': continue
                #     elif s[0]=='-':
                #         print(u'Delete "{}" from position {}'.format(s[-1],i))
                #     elif s[0]=='+':
                #         print(u'Add "{}" to position {}'.format(s[-1],i))

            results = [
                r.inner for r in self.cache.relations.values()
                # if (lowercase(r.schema) == schema)
                if (lowercase(r.schema) == schema and
                    lowercase(r.database) == database)
            ]
            logger.info(f"results: {results}")

            return self.cache.get_relations(database, schema)

        schema_relation = self.Relation.create(
            database=database,
            schema=schema,
            identifier='',
            quote_policy=self.config.quoting
        ).without_identifier()

        # we can't build the relations cache because we don't have a
        # manifest so we can't run any operations.
        relations = self.list_relations_without_caching(
            schema_relation
        )

        logger.info('with database={}, schema={}, relations={}'
                     .format(database, schema, relations))
        return relations

    def _make_match_kwargs(
        self, database: str, schema: str, identifier: str
    ) -> Dict[str, str]:
        quoting = self.config.quoting
        if identifier is not None and quoting['identifier'] is False:
            identifier = identifier.lower()

        if schema is not None and quoting['schema'] is False:
            schema = schema.lower()

        if database is not None and quoting['database'] is False:
            database = database.lower()

        # def filter_null_values(input: Dict[K_T, Optional[V_T]]) -> Dict[K_T, V_T]:
        #     return {k: v for k, v in input.items() if v is not None}
        #
        # return filter_null_values({
        #     'database': database,
        #     'identifier': identifier,
        #     'schema': schema,
        # })

        return {
            'database': database,
            'identifier': identifier,
            'schema': schema,
        }

    def _make_match(
        self,
        relations_list: List[BaseRelation],
        database: str,
        schema: str,
        identifier: str,
    ) -> List[BaseRelation]:

        logger.info(f"Start _make_match({database}, {schema}, {identifier})")
        matches = []

        search = self._make_match_kwargs(database, schema, identifier)

        logger.info(f"Try to match search {search}")
        logger.info(f"relations_list: {relations_list}")

        for relation in relations_list:
            logger.info(f"{relation}.matches(**{search}) = {relation.matches(**search)}")

            if relation.matches(**search):
                matches.append(relation)

        return matches

    # from dbt.adapters.base.meta import available
    # @available.parse_none
    def get_relation(
        self, database: str, schema: str, identifier: str
    ) -> Optional[BaseRelation]:
        print("Start get_relation")
        logger.info(f"Start get_relation({database}, {schema}, {identifier})")

        relations_list = self.list_relations(database, schema)

        print(f"relations_list: {relations_list}")
        logger.info(f"relations_list: {relations_list}")

        matches = self._make_match(relations_list, database, schema,
                                   identifier)

        print(f"matches: {matches}")
        logger.info(f"matches: {matches}")

        if len(matches) > 1:
            kwargs = {
                'identifier': identifier,
                'schema': schema,
                'database': database,
            }
            get_relation_returned_multiple_results(
                kwargs, matches
            )

        elif matches:
            return matches[0]

        return None

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

    def get_catalog(
        self, manifest: Manifest
    ) -> Tuple[agate.Table, List[Exception]]:
        schema_map = self._get_catalog_schemas(manifest)

        print("schema_map:")
        print(schema_map)

        with executor(self.config) as tpe:
            futures: List[Future[agate.Table]] = []
            for info, schemas in schema_map.items():
                if len(schemas) == 0:
                    continue
                name = '.'.join([
                    str(info.database),
                    'information_schema'
                ])

                fut = tpe.submit_connected(
                    self, name,
                    self._get_one_catalog, info, schemas, manifest
                )
                futures.append(fut)

            catalogs, exceptions = catch_as_completed(futures)

        print("catalogs:")
        print(catalogs)
        print(catalogs.print_table())


        print("exceptions:")
        print(exceptions)

        #-------------------------------------------
        # @TODO Remove this when done troubleshooting

        catalog_table = catalogs

        def _coerce_decimal(value):
            if isinstance(value, dbt.utils.DECIMALS):
                return float(value)
            return value

        catalog_data: List[PrimitiveDict] = [
            dict(zip(catalog_table.column_names, map(_coerce_decimal, row)))
            for row in catalog_table
        ]

        catalog = Catalog(catalog_data)

        print("catalog_data:")
        print(catalog_data)
        #-------------------------------------------

        return catalogs, exceptions

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

def catch_as_completed(
    futures  # typing: List[Future[agate.Table]]
) -> Tuple[agate.Table, List[Exception]]:

    # catalogs: agate.Table = agate.Table(rows=[])
    tables: List[agate.Table] = []
    exceptions: List[Exception] = []

    for future in as_completed(futures):
        exc = future.exception()
        # we want to re-raise on ctrl+c and BaseException
        if exc is None:
            catalog = future.result()
            tables.append(catalog)
        elif (
            isinstance(exc, KeyboardInterrupt) or
            not isinstance(exc, Exception)
        ):
            raise exc
        else:
            warn_or_error(
                f'Encountered an error while generating catalog: {str(exc)}'
            )
            # exc is not None, derives from Exception, and isn't ctrl+c
            exceptions.append(exc)
    return merge_tables(tables), exceptions
