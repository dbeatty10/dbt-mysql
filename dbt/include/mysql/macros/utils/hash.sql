{% macro mysql__hash(field) -%}

    md5(cast({{ field }} as char))

{%- endmacro %}
