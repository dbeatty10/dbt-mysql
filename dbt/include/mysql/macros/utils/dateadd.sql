{% macro mysql__dateadd(datepart, interval, from_date_or_timestamp) %}

    timestampadd(
        {{ datepart }},
        {{ interval }},
        {{ from_date_or_timestamp }}
    )

{% endmacro %}
