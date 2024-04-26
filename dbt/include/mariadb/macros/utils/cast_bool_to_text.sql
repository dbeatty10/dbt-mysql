{% macro mariadb__cast_bool_to_text(field) %}

    case when {{ field }} = 1 then 'true' else 'false' end

{% endmacro %}
