
{% macro incremental_delete(tmp_relation, target_relation, unique_key=none, statement_name="pre_main") %}
    {%- if unique_key is not none and unique_key|length -%}
    delete
    from {{ target_relation }}
    where ({{ unique_key if unique_key is string else unique_key | join(',') }}) in (
        select {{ unique_key if unique_key is string else unique_key | join(',') }}
        from {{ tmp_relation }}
    )
    {%- endif %}

{%- endmacro %}

{% macro incremental_insert(tmp_relation, target_relation, unique_key=none, statement_name="main") %}
    {%- set dest_columns = adapter.get_columns_in_relation(target_relation) -%}
    {%- set dest_cols_csv = dest_columns | map(attribute='quoted') | join(', ') -%}

    insert into {{ target_relation }} ({{ dest_cols_csv }})
    (
       select {{ dest_cols_csv }}
       from {{ tmp_relation }}
    )
{%- endmacro %}
