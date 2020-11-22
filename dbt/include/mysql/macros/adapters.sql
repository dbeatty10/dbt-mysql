
{% macro mysql__list_schemas(database) %}
    {{ log("logger: start mysql__list_schemas", info=True) }}
    {% call statement('list_schemas', fetch_result=True, auto_begin=False) -%}
        select distinct schema_name
        from information_schema.schemata
    {%- endcall %}

    {{ return(load_result('list_schemas').table) }}
{% endmacro %}

{% macro mysql__create_schema(relation) -%}
  {{ log("logger: start mysql__create_schema(" ~ relation ~ ")", info=True) }}
  {%- call statement('create_schema') -%}
    create schema if not exists {{ relation.without_identifier() }}
  {%- endcall -%}
{% endmacro %}

{% macro mysql__drop_schema(relation) -%}
  {{ log("logger: start mysql__drop_schema", info=True) }}
  {%- call statement('drop_schema') -%}
    drop schema if exists {{ relation.without_identifier() }}
  {% endcall %}
{% endmacro %}

{% macro mysql__drop_relation(relation) -%}
    {{ log("logger: start mysql__drop_relation", info=True) }}
    {% call statement('drop_relation', auto_begin=False) -%}
        drop {{ relation.type }} if exists {{ relation }}
    {%- endcall %}
{% endmacro %}

{% macro mysql__truncate_relation(relation) -%}
    {{ log("logger: start mysql__truncate_relation", info=True) }}
    {% call statement('truncate_relation') -%}
      truncate table {{ relation }}
    {%- endcall %}
{% endmacro %}

{#-- We can't use temporary tables with `create ... as ()` syntax #}
{% macro create_temporary_view(relation, sql) -%}
  create temporary view {{ relation.include(schema=false) }} as
    {{ sql }}
{% endmacro %}

{% macro XXXX_mysql__create_table_as(temporary, relation, sql) -%}
  {{ log("logger: start mysql__create_table_as", info=True) }}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}

  {% if temporary -%}
    {{ create_temporary_view(relation, sql) }}
  {%- else -%}
    create {% if temporary: -%}temporary{%- endif %} table
      {{ relation.include(database=False, schema=(not temporary)) }}
    as (
      {{ sql }}
    );
  {%- endif %}
{% endmacro %}

{% macro mysql__create_table_as(temporary, relation, sql) -%}
  {{ log("logger: start mysql__create_table_as", info=True) }}
  {% if temporary: -%}
    {{ log("logger: temporary = " ~ temporary, info=True) }}
  {%- endif %}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}

  -- create table
  create {% if temporary: -%}temporary{%- endif %} table
    {{ relation.include(database=False) }}
  as (
    {{ sql }}
  );
{% endmacro %}

{% macro mysql__current_timestamp() -%}
  current_timestamp()
{%- endmacro %}

{% macro mysql__rename_relation(from_relation, to_relation) -%}
  {{ log("logger: start mysql__rename_relation", info=True) }}
  {#
    MySQL rename fails when the relation already exists, so a 2-step process is needed:
    1. Drop the existing relation
    2. Rename the new relation to existing relation
  #}
  {% call statement('drop_relation') %}
    drop {{ to_relation.type }} if exists {{ to_relation }} cascade
  {% endcall %}
  {% call statement('rename_relation') %}
    rename table {{ from_relation }} to {{ to_relation }}
  {% endcall %}
{% endmacro %}

{% macro mysql__check_schema_exists(database, schema) -%}
    {{ log("logger: start mysql__check_schema_exists", info=True) }}
    {# no-op #}
    {# see MySQLAdapter.check_schema_exists() #}
{% endmacro %}

-- mysql__get_columns_in_relation
-- original__mysql__get_columns_in_relation
{% macro original__mysql__get_columns_in_relation(relation) -%}
    {{ log("logger: start original__mysql__get_columns_in_relation (001)", info=True) }}
    {% call statement('get_columns_in_relation', fetch_result=True) %}
        select
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        from
            information_schema.columns
        where
            table_schema = '{{ relation.schema }}'
            and table_name = '{{ relation.identifier }}'
    {% endcall %}

    {% set table = load_result('get_columns_in_relation').table %}
    {{ table.print_table() }}
    {% set results = sql_convert_columns_in_relation(table) %}
    {{ log("logger: results (001) = " ~ results, info=True) }}
    {{ return(results) }}
{% endmacro %}

-- mysql__get_columns_in_relation
-- new__mysql__get_columns_in_relation
{% macro mysql__get_columns_in_relation(relation) -%}
    {{ log("logger: start mysql__get_columns_in_relation (002)", info=True) }}
    {% call statement('get_columns_in_relation', fetch_result=True) %}
        show columns from {{ relation.schema }}.{{ relation.identifier }}
    {% endcall %}

    {% set table = load_result('get_columns_in_relation').table %}
    {{ table.print_table() }}
    {% set results = sql_convert_columns_in_relation(table) %}
    {{ log("logger: results (002) = " ~ results, info=True) }}
    {{ return(results) }}
{% endmacro %}

{% macro mysql__list_relations_without_caching(schema_relation) %}
  {{ log("logger: start mysql__list_relations_without_caching", info=True) }}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    select
      -- table_catalog as "database",
      null as "database",
      table_name as name,
      table_schema as "schema",
      case when table_type = 'BASE TABLE' then 'table'
           when table_type = 'VIEW' then 'view'
           else table_type
      end as table_type
    from information_schema.tables
    where table_schema = '{{ schema_relation.schema }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}

{% macro mysql__generate_database_name(custom_database_name=none, node=none) -%}
  {{ log("logger: start mysql__generate_database_name", info=True) }}
  {% do return(None) %}
{%- endmacro %}
