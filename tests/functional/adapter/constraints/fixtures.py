# model breaking constraints
my_model_with_nulls_sql = """
{{
  config(
    materialized = "table"
  )
}}

select
  -- null value for 'id'
  CAST(null AS UNSIGNED) as id,
  -- change the color as well (to test rollback)
  'red' as color,
  '2019-01-01' as date_day
"""


my_model_view_with_nulls_sql = """
{{
  config(
    materialized = "view"
  )
}}

select
  -- null value for 'id'
  CAST(null AS UNSIGNED) as id,
  -- change the color as well (to test rollback)
  'red' as color,
  '2019-01-01' as date_day
"""

my_model_incremental_with_nulls_sql = """
{{
  config(
    materialized = "incremental",
    on_schema_change='append_new_columns'  )
}}

select
  -- null value for 'id'
  CAST(null AS UNSIGNED) as id,
  -- change the color as well (to test rollback)
  'red' as color,
  '2019-01-01' as date_day
"""

# model columns data types different to schema definitions
my_model_contract_sql_header_sql = """
{{
  config(
    materialized = "table"
  )
}}

select 'Kolkata' as column_name
"""

my_model_incremental_contract_sql_header_sql = """
{{
  config(
    materialized = "incremental",
    on_schema_change="append_new_columns"
  )
}}

select 'Kolkata' as column_name
"""

constrained_model_schema_yml = """
version: 2
models:
  - name: my_model
    config:
      contract:
        enforced: true
    constraints:
      - type: check
        expression: (id > 0)
      - type: check
        expression: id >= 1
      - type: primary_key
        columns: [ id ]
      - type: unique
        columns: [ color(10), date_day(20) ]
        name: strange_uniqueness_requirement
      - type: foreign_key
        columns: [ id ]
        expression: {schema}.foreign_key_model (id)
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: foreign_key_model
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        constraints:
          - type: unique
          - type: primary_key
"""

model_quoted_column_schema_yml = """
version: 2
models:
  - name: my_model
    config:
      contract:
        enforced: true
      materialized: table
    constraints:
      - type: check
        # this one is the on the user
        expression: (`from` = 'blue')
        columns: [ '`from`' ]
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
        tests:
          - unique
      - name: from  # reserved word
        quote: true
        data_type: text
        constraints:
          - type: not_null
      - name: date_day
        data_type: text
"""

# MariaDB does not support multiple column-level CHECK constraints
mariadb_model_schema_yml = """
version: 2
models:
  - name: my_model
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: id > 0 AND id >= 1
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: my_model_error
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: my_model_wrong_order
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: my_model_wrong_name
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
"""

# MariaDB does not support multiple column-level CHECK constraints
# Additionally, MariaDB requires CHECK constraints to come last
mariadb_model_fk_constraint_schema_yml = """
version: 2
models:
  - name: my_model
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: foreign_key
            expression: {schema}.foreign_key_model (id)
          - type: unique
          - type: check
            expression: id > 0 AND id >= 1
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: my_model_error
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: my_model_wrong_order
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: my_model_wrong_name
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: text
      - name: date_day
        data_type: text
  - name: foreign_key_model
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        constraints:
          - type: unique
          - type: primary_key
"""
