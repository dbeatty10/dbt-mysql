
{% macro old_1__mysql__snapshot_merge_sql(target, source, insert_cols) -%}
    {{ log("logger: start mysql__snapshot_merge_sql(" ~ target ~ ", " ~ source ~ ", " ~ insert_cols ~ ")", info=True) }}
    {%- set insert_cols_csv = insert_cols | join(', ') -%}

    merge into {{ target }} as DBT_INTERNAL_DEST
    using {{ source }} as DBT_INTERNAL_SOURCE
    on DBT_INTERNAL_SOURCE.dbt_scd_id = DBT_INTERNAL_DEST.dbt_scd_id

    when matched
     and DBT_INTERNAL_DEST.dbt_valid_to is null
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'update'
        then update
        set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to

    when matched
     and DBT_INTERNAL_DEST.dbt_valid_to is null
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'delete'
        then update
        set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to

    when not matched
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'insert'
        then insert ({{ insert_cols_csv }})
        values ({{ insert_cols_csv }})
    ;
{% endmacro %}

{% macro old_2__mysql__snapshot_merge_sql(target, source, insert_cols) -%}

    merge into {{ target }} as DBT_INTERNAL_DEST
    using {{ source }} as DBT_INTERNAL_SOURCE
    on DBT_INTERNAL_SOURCE.dbt_scd_id = DBT_INTERNAL_DEST.dbt_scd_id

    when matched
     and DBT_INTERNAL_DEST.dbt_valid_to is null
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'update'
        then update
        set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to

    when matched
     and DBT_INTERNAL_DEST.dbt_valid_to is null
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'delete'
        then update
        set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to

    when not matched
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'insert'
        then insert *
    ;
{% endmacro %}


{% macro xxx_mysql__snapshot_merge_sql_update(target, source, insert_cols) -%}
    {%- set insert_cols_csv = insert_cols | join(', ') -%}

    update {{ target }}
    set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to
    from {{ source }} as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_scd_id = {{ target }}.dbt_scd_id
      and DBT_INTERNAL_SOURCE.dbt_change_type = 'update'
      and {{ target }}.dbt_valid_to is null
{% endmacro %}


{% macro mysql__snapshot_merge_sql_update(target, source, insert_cols) -%}
    update {{ target }}, (select dbt_scd_id, dbt_change_type, dbt_valid_to from {{ source }}) as DBT_INTERNAL_SOURCE
    set {{ target }}.dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to
    where DBT_INTERNAL_SOURCE.dbt_scd_id = {{ target }}.dbt_scd_id
    and DBT_INTERNAL_SOURCE.dbt_change_type = 'update'
    and {{ target }}.dbt_valid_to is null
{% endmacro %}


{% macro mysql__snapshot_merge_sql_insert(target, source, insert_cols) -%}
    {%- set insert_cols_csv = insert_cols | join(', ') -%}

    insert into {{ target }} ({{ insert_cols_csv }})
    select {% for column in insert_cols -%}
        DBT_INTERNAL_SOURCE.{{ column }} {%- if not loop.last %}, {%- endif %}
    {%- endfor %}
    from {{ source }} as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_change_type = 'insert'
{% endmacro %}
