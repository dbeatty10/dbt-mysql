
{% macro mysql__snapshot_string_as_time(timestamp) -%}
    {{ log("logger: mysql__snapshot_string_as_time(" ~ timestamp ~ ")", info=True) }}

    {# 2020-11-21 01:07:19 #}
    {%- set result = "str_to_date('" ~ timestamp ~ "', '%Y-%m-%d %T')" -%}
    {{ return(result) }}
{%- endmacro %}

{% materialization snapshot, adapter='mysql' %}
  {%- set config = model['config'] -%}

  {%- set target_table = model.get('alias', model.get('name')) -%}

  {%- set strategy_name = config.get('strategy') -%}
  {%- set unique_key = config.get('unique_key') %}

  {% if not adapter.check_schema_exists(model.database, model.schema) %}
    {% do create_schema(model.database, model.schema) %}
  {% endif %}

  {% set target_relation_exists, target_relation = get_or_create_relation(
          database=none,
          schema=model.schema,
          identifier=target_table,
          type='table') -%}

  {%- if not target_relation.is_table -%}
    {% do exceptions.relation_wrong_type(target_relation, 'table') %}
  {%- endif -%}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {{ log("strategy_name: " ~ strategy_name, info=True) }}
  {{ log("strategy_macro: strategy_dispatch(" ~ strategy_name ~ ")", info=True) }}
  {% set strategy_macro = strategy_dispatch(strategy_name) %}
  {{ log("strategy_macro: " ~ strategy_macro, info=True) }}
  {% set strategy = strategy_macro(model, "snapshotted_data", "source_data", config, target_relation_exists) %}
  {{ log("strategy: " ~ strategy, info=True) }}

  {% if not target_relation_exists %}

      {% set build_sql = build_snapshot_table(strategy, model['injected_sql']) %}
      {% set final_sql = create_table_as(False, target_relation, build_sql) %}

      {% call statement('main') %}
          {{ final_sql }}
      {% endcall %}

  {% else %}

      {{ adapter.valid_snapshot_target(target_relation) }}

      {% set staging_table = build_snapshot_staging_table(strategy, sql, target_relation) %}

      -- this may no-op if the database does not require column expansion
      {% do adapter.expand_target_column_types(from_relation=staging_table,
                                               to_relation=target_relation) %}

      {% set missing_columns = adapter.get_missing_columns(staging_table, target_relation)
                                   | rejectattr('name', 'equalto', 'dbt_change_type')
                                   | rejectattr('name', 'equalto', 'DBT_CHANGE_TYPE')
                                   | rejectattr('name', 'equalto', 'dbt_unique_key')
                                   | rejectattr('name', 'equalto', 'DBT_UNIQUE_KEY')
                                   | list %}

      {% do create_columns(target_relation, missing_columns) %}

      {% set source_columns = adapter.get_columns_in_relation(staging_table)
                                   | rejectattr('name', 'equalto', 'dbt_change_type')
                                   | rejectattr('name', 'equalto', 'DBT_CHANGE_TYPE')
                                   | rejectattr('name', 'equalto', 'dbt_unique_key')
                                   | rejectattr('name', 'equalto', 'DBT_UNIQUE_KEY')
                                   | list %}

      {% set quoted_source_columns = [] %}
      {% for column in source_columns %}
        {% do quoted_source_columns.append(adapter.quote(column.name)) %}
      {% endfor %}

      {{ log("logger: materialization snapshot, adapter='mysql' missing_columns= " ~ missing_columns ~ "", info=True) }}
      {{ log("logger: materialization snapshot, adapter='mysql' source_columns= " ~ source_columns ~ "", info=True) }}
      {{ log("logger: materialization snapshot, adapter='mysql' quoted_source_columns= " ~ quoted_source_columns ~ "", info=True) }}

      -- MySQL does not support the MERGE statement, so need to use seperate UPDATE + INSERT instead
      {% set final_sql_update = mysql__snapshot_merge_sql_update(
            target = target_relation,
            source = staging_table,
            insert_cols = quoted_source_columns
         )
      %}

      {{ log(final_sql_update, info=True) }}

      {% set final_sql_insert = mysql__snapshot_merge_sql_insert(
            target = target_relation,
            source = staging_table,
            insert_cols = quoted_source_columns
         )
      %}

      {{ log(final_sql_insert, info=True) }}

      {% call statement('main') %}
          {{ final_sql_update }}
      {% endcall %}

      {% call statement('main') %}
          {{ final_sql_insert }}
      {% endcall %}

  {% endif %}

  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {{ adapter.commit() }}

  {% if staging_table is defined %}
      {% do post_snapshot(staging_table) %}
  {% endif %}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({'relations': [target_relation]}) }}

{% endmaterialization %}

{% macro snapshot_check_all_get_existing_columns(node, target_exists) -%}
    {{ log("logger: snapshot_check_all_get_existing_columns(" ~ node ~ "," ~ target_exists ~ ")", info=True) }}
    {%- set query_columns = get_columns_in_query(node['compiled_sql']) -%}
    {{ log("logger: query_columns = " ~ query_columns ~ "", info=True) }}
    {%- if not target_exists -%}
        {# no table yet -> return whatever the query does #}
        {{ return([false, query_columns]) }}
    {%- endif -%}
    {# handle any schema changes #}
    {%- set target_table = node.get('alias', node.get('name')) -%}
    -- { %- set target_relation = adapter.get_relation(database=node.database, schema=node.schema, identifier=target_table) -%}
    {%- set target_relation = adapter.get_relation(database=None, schema=node.schema, identifier=target_table) -%}
    {%- set existing_cols = get_columns_in_query('select * from ' ~ target_relation) -%}
    {%- set ns = namespace() -%} {# handle for-loop scoping with a namespace #}
    {%- set ns.column_added = false -%}

    {%- set intersection = [] -%}
    {%- for col in query_columns -%}
        {%- if col in existing_cols -%}
            {%- do intersection.append(col) -%}
        {%- else -%}
            {% set ns.column_added = true %}
        {%- endif -%}
    {%- endfor -%}
    {{ log("logger: ns.column_added = " ~ ns.column_added ~ "", info=True) }}
    {{ log("logger: intersection = " ~ intersection ~ "", info=True) }}
    {{ return([ns.column_added, intersection]) }}
{%- endmacro %}
