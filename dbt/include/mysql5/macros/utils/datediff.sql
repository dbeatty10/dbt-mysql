{% macro mysql5__datediff(first_date, second_date, datepart) -%}

    {% if datepart == 'year' %}
        (year({{second_date}}) - year({{first_date}}))
    {% elif datepart == 'quarter' %}
        ({{ datediff(first_date, second_date, 'year') }} * 4 + quarter({{second_date}}) - quarter({{first_date}}))
    {% elif datepart == 'month' %}
        ({{ datediff(first_date, second_date, 'year') }} * 12 + month({{second_date}}) - month({{first_date}}))
    {% elif datepart == 'day' %}
        datediff({{second_date}}, {{first_date}})
    {% elif datepart == 'week' %}
        truncate({{ datediff(first_date, second_date, 'day') }} / 7 + case
            when dayofweek({{first_date}}) <= dayofweek({{second_date}}) then
                case when {{first_date}} <= {{second_date}} then 0 else -1 end
            else
                case when {{first_date}} <= {{second_date}} then 1 else 0 end
        end, 0)
    {% elif datepart == 'hour' %}
        ({{ datediff(first_date, second_date, 'day') }} * 24 + hour({{second_date}}) - hour({{first_date}}))
    {% elif datepart == 'minute' %}
        ({{ datediff(first_date, second_date, 'hour') }} * 60 + minute({{second_date}}) - minute({{first_date}}))
    {% elif datepart == 'second' %}
        ({{ datediff(first_date, second_date, 'minute') }} * 60 + floor(second({{second_date}})) - floor(second({{first_date}})))
    {% elif datepart == 'millisecond' %}
        ({{ datediff(first_date, second_date, 'second') }} * 1000 + floor(microsecond({{second_date}} / 1000)) - floor(microsecond({{first_date}}) / 1000))
    {% elif datepart == 'microsecond' %}
        ({{ datediff(first_date, second_date, 'second') }} * 1000000 + floor(microsecond({{second_date}})) - floor(microsecond({{first_date}})))
    {% else %}
        {{ exceptions.raise_compiler_error("Unsupported datepart for macro datediff in mysql5: {!r}".format(datepart)) }}
    {% endif %}

{%- endmacro %}
