{% macro mariadb__listagg(measure, delimiter_text, order_by_clause, limit_num) -%}

    group_concat(
        {{ measure }}
        {% if order_by_clause -%}
           {{ order_by_clause }}
        {%- endif %}
        {% if delimiter_text -%}
            separator {{ delimiter_text }}
        {%- endif %}
        {% if limit_num -%}
            limit {{ limit_num }}
        {%- endif %}
    )

{%- endmacro %}
