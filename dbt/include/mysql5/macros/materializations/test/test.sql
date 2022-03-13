{% macro mysql5__get_test_sql(main_sql, fail_calc, warn_if, error_if, limit) -%}
    SELECT
      {{ fail_calc }} as failures,
      CASE
      	WHEN {{ fail_calc }} {{ warn_if | replace("!=","<>") }} THEN 'true'
      	ELSE 'false'
      END AS should_warn,
      CASE
      	WHEN {{ fail_calc }} {{ error_if | replace("!=","<>") }} THEN 'true'
      	ELSE 'false'
      END AS should_error
    FROM (
      {{ main_sql }}
      {{ "limit " ~ limit if limit != none }}
    ) dbt_internal_test
{%- endmacro %}