## dbt-mysql 0.19.0 (TBD)

- Manage MySQL connections via a self-contained DB API 2.0 compliant Python driver (instead of ODBC) ([#38](https://github.com/dbeatty10/dbt-mysql/pull/38))
- Integration tests via (custom) dbt-adapter-tests ([#45](https://github.com/dbeatty10/dbt-mysql/pull/45))
- Split into two separate adapters for MySQL 5.x and 8.x ([#46](https://github.com/dbeatty10/dbt-mysql/pull/46))

## dbt-mysql 0.18.1 (December 6, 2020)

## dbt-mysql 0.18.0 (December 6, 2020)

### Under the hood
- Support for MySQL 5.6, 5.7, and 8.0 ([#24](https://github.com/dbeatty10/dbt-mysql/pull/24))
- Manage MySQL connections via ODBC ([#1](https://github.com/dbeatty10/dbt-mysql/pull/1))
- Pass [dbt-adapter-tests](https://github.com/dbeatty10/dbt-adapter-tests) ([#3](https://github.com/dbeatty10/dbt-mysql/pull/3))
- Apache 2.0 license and instructions for project contributors, README, and release instructions ([#2](https://github.com/dbeatty10/dbt-mysql/pull/2), [#12](https://github.com/dbeatty10/dbt-mysql/pull/12), [#17](https://github.com/dbeatty10/dbt-mysql/pull/17))
- Add issue templates and CHANGELOG ([#18](https://github.com/dbeatty10/dbt-mysql/pull/18))
- Support case-sensitive identifiers (schemas, tables/views, and columns) ([#26](https://github.com/dbeatty10/dbt-mysql/pull/26))
