{% macro mariadb__bool_or(expression) -%}

    max(case when {{ expression }} then 1 else 0 end)

{%- endmacro %}
