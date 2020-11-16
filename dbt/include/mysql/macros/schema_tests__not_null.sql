
{% macro mysql__test_not_null(model) %}

{% set column_name = kwargs.get('column_name', kwargs.get('arg')) %}

select count(*) as validation_errors
from {{ model.include(database=False) }}
where {{ column_name }} is null

{% endmacro %}
