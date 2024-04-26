{% macro mysql5__listagg(measure, delimiter_text, order_by_clause, limit_num) -%}

    {% if limit_num -%}
        substring_index(
    {%- endif %}
    group_concat(
        {{ measure }}
        {% if order_by_clause -%}
           {{ order_by_clause }}
        {%- endif %}
        {% if delimiter_text -%}
            separator {{ delimiter_text }}
        {%- endif %}
    )
    {% if limit_num -%}
        , {{ delimiter_text }}, {{ limit_num }})
    {%- endif %}

{%- endmacro %}
