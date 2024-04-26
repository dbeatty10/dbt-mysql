{% macro mysql5__date_trunc(datepart, date) -%}

    {% if datepart == 'year' %}
        date_format({{ date }}, '%Y-01-01')
    {% elif datepart == 'quarter' %}
        case
            when month({{ date }}) between 1 and 3 then
                {{ date_trunc('year', date) }}
            when month({{ date }}) between 4 and 6 then
                date_add({{ date_trunc('year', date) }}, interval 3 month)
            when month({{ date }}) between 7 and 9 then
                date_add({{ date_trunc('year', date) }}, interval 6 month)
            when month({{ date }}) between 10 and 12 then
                date_add({{ date_trunc('year', date) }}, interval 9 month)
        end
    {% elif datepart == 'month' %}
        date_format({{ date }}, '%Y-%m-01')
    {% elif datepart == 'day' %}
        date_format({{ date }}, '%Y-%m-%d')
    {% elif datepart == 'hour' %}
        date_format({{ date }}, '%Y-%m-%d %h:00:00')
    {% elif datepart == 'minute' %}
        date_format({{ date }}, '%Y-%m-%d %h:%i:00')
    {% elif datepart == 'second' %}
        date_format({{ date }}, '%Y-%m-%d %h:%i:%s')
    {% else %}
        {{ exceptions.raise_compiler_error("Unsupported datepart for macro date_trunc in mysql5: {!r}".format(datepart)) }}
    {% endif %}

{%- endmacro %}
