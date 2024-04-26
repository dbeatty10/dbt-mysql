models__test_dateadd_sql = """
with data as (

    select * from {{ ref('data_dateadd') }}

)

select
    case
        when datepart = 'hour' then {{ dateadd('hour', 'interval_length', 'from_time') }}
        when datepart = 'day' then {{ dateadd('day', 'interval_length', 'from_time') }}
        when datepart = 'month' then {{ dateadd('month', 'interval_length', 'from_time') }}
        when datepart = 'year' then {{ dateadd('year', 'interval_length', 'from_time') }}
        else null
    end as actual,
    result as expected

from data
"""

models__test_safe_cast_sql = """
with data as (

    select * from {{ ref('data_safe_cast') }}

)

select
    {{ safe_cast('field', 'char') }} as actual,
    output as expected

from data
"""
