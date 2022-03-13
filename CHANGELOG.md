## Unreleased (TBD)
- Support dbt v0.20.2 ([#88](https://github.com/dbeatty10/dbt-mysql/pull/88))

## dbt-mysql 0.20.1 (March 13, 2022)
- Remove integration tests and docs for MySQL 5.6 ([#74](https://github.com/dbeatty10/dbt-mysql/issues/74), [#86](https://github.com/dbeatty10/dbt-mysql/pull/86))
- Support dbt v0.20.1 ([#87](https://github.com/dbeatty10/dbt-mysql/pull/87))

## dbt-mysql 0.20.0 (March 13, 2022)
- Support dbt v0.20.0 ([#83](https://github.com/dbeatty10/dbt-mysql/pull/83))
- Report status as `SUCCESS` instead of `Unknown cursor state/status` ([#84](https://github.com/dbeatty10/dbt-mysql/pull/84))

## dbt-mysql 0.19.2 (March 12, 2022)
- Support dbt v0.19.2 ([#81](https://github.com/dbeatty10/dbt-mysql/pull/81))

## dbt-mysql 0.19.1 (March 6, 2022)
### Under the hood
- Integration tests for MySQL 5.7 ([#70](https://github.com/dbeatty10/dbt-mysql/issues/70), [#71](https://github.com/dbeatty10/dbt-mysql/pull/71))
- Integration tests for MariaDB 10.5 ([#72](https://github.com/dbeatty10/dbt-mysql/pull/72))
- Support for MariaDB 10.5 ([#32](https://github.com/dbeatty10/dbt-mysql/issues/32), [#73](https://github.com/dbeatty10/dbt-mysql/pull/73))
- Enable snapshot integration tests for MySQL 5.7 and MariaDB 10.5 ([#75](https://github.com/dbeatty10/dbt-mysql/issues/75), [#76](https://github.com/dbeatty10/dbt-mysql/pull/76))
- Support dbt v0.19.1 ([#80](https://github.com/dbeatty10/dbt-mysql/pull/80))

## dbt-mysql 0.19.0.1 (February 19, 2022)
- Optional `ssl_disabled` property ([#67](https://github.com/dbeatty10/dbt-mysql/pull/67))

## dbt-mysql 0.19.0.1rc1 (February 16, 2022)

### Under the hood
- Continuous integration using CircleCI ([#8](https://github.com/dbeatty10/dbt-mysql/issues/8), [#60](https://github.com/dbeatty10/dbt-mysql/pull/60))

### Fixes
- Execute incremental upsert queries separately ([#62](https://github.com/dbeatty10/dbt-mysql/issues/62), [#69](https://github.com/dbeatty10/dbt-mysql/pull/69))

## dbt-mysql 0.19.0 (February 3, 2021)
- Latest versions of dbt (0.19.0) and dbt-adapter-tests (4.0) ([#53](https://github.com/dbeatty10/dbt-mysql/pull/53))

## dbt-mysql 0.19.0rc1 (January 3, 2021)

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
