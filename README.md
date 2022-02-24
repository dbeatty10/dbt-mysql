# dbt-mysql

This plugin ports [dbt](https://getdbt.com) functionality to MySQL and MariaDB.

This is an experimental plugin:
- We have not tested it extensively
- Storage engines other than the default of InnoDB are untested
- Only tested with [dbt-adapter-tests](https://github.com/fishtown-analytics/dbt-adapter-tests) with the following:
  - MySQL 5.6
  - MySQL 5.7
  - MySQL 8.0
  - MariaDB 10.5
- Compatiblity with other [dbt packages](https://hub.getdbt.com/) (like [dbt_utils](https://hub.getdbt.com/fishtown-analytics/dbt_utils/latest/)) is also untested

Please read these docs carefully and use at your own risk. [Issues](https://github.com/dbeatty10/dbt-mysql/issues/new) and [PRs](https://github.com/dbeatty10/dbt-mysql/blob/main/CONTRIBUTING.rst#contributing) welcome!

Table of Contents
=================

   * [Installation](#installation)
   * [Supported features](#supported-features)
      * [MySQL 8.0](#mysql-80)
      * [MySQL 5.6 and 5.7](#mysql-56-and-57)
         * [MySQL 5.6 configuration gotchas](#mysql-56-configuration-gotchas)
         * [MySQL 5.7 configuration gotchas](#mysql-57-configuration-gotchas)
   * [Configuring your profile](#configuring-your-profile)
   * [Notes](#notes)
   * [Running Tests](#running-tests)
   * [Reporting bugs and contributing code](#reporting-bugs-and-contributing-code)

### Installation
This plugin can be installed via pip:

```bash
$ pip install dbt-mysql
```

### Supported features

| MariaDB 10.5 | MySQL 5.6 / 5.7 | MySQL 8.0 | Feature                     |
|:---------:|:---------:|:---:|-----------------------------|
|     ✅     |     ✅     |  ✅  | Table materialization       |
|     ✅     |     ✅     |  ✅  | View materialization        |
|     ✅     |     ✅     |  ✅  | Incremental materialization |
|     ✅     |     ❌     |  ✅  | Ephemeral materialization   |
|     ✅     |     ✅     |  ✅  | Seeds                       |
|     ✅     |     ✅     |  ✅  | Sources                     |
|     ✅     |     ✅     |  ✅  | Custom data tests           |
|     ✅     |     ✅     |  ✅  | Docs generate               |
|     🤷     |     🤷     |  ✅  | Snapshots                   |

Notes:
- Ephemeral materializations rely upon [Common Table Expressions](https://en.wikipedia.org/wiki/Hierarchical_and_recursive_queries_in_SQL) (CTEs), which are not supported until MySQL 8.0
- MySQL 5.6 and 5.7 have some configuration gotchas that affect snapshots (see below).

##### MySQL 5.6 configuration gotchas

dbt snapshots might not work properly due to [automatic initialization and updating for `TIMESTAMP`](https://dev.mysql.com/doc/refman/5.6/en/timestamp-initialization.html) if:
- the output of `SHOW VARIABLES LIKE 'sql_mode'` includes `NO_ZERO_DATE`
- the output of `SHOW GLOBAL VARIABLES LIKE 'explicit_defaults_for_timestamp'` has a value of `OFF`

A solution is to include the following in a `*.cnf` file:
```
[mysqld]
explicit_defaults_for_timestamp = true
```

##### MySQL 5.7 configuration gotchas

dbt snapshots might not work properly due to [automatic initialization and updating for `TIMESTAMP`](https://dev.mysql.com/doc/refman/5.7/en/timestamp-initialization.html) if:
- the output of `SHOW VARIABLES LIKE 'sql_mode'` includes `NO_ZERO_DATE`

A solution is to include the following in a `*.cnf` file:
```
[mysqld]
explicit_defaults_for_timestamp = true
sql_mode = "ALLOW_INVALID_DATES,{other_sql_modes}"
```
where `{other_sql_modes}` is the rest of the modes from the `SHOW VARIABLES LIKE 'sql_mode'` output.

### Configuring your profile

A dbt profile can be configured to run against MySQL using configuration example below.

Use `type: mysql` for MySQL 8.x, `type: mysql5` for MySQL 5.x, and `type: mariadb` for MariaDB.

**Example entry for profiles.yml:**

```
your_profile_name:
  target: dev
  outputs:
    dev:
      type: mysql
      server: localhost
      port: 3306
      schema: analytics
      username: your_mysql_username
      password: your_mysql_password
      ssl_disabled: True
```

| Option          | Description                                                                         | Required?                                                          | Example                                        |
| --------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| type            | The specific adapter to use                                                         | Required                                                           | `mysql`, `mysql5` or `mariadb`                            |
| server          | The server (hostname) to connect to                                                 | Required                                                           | `yourorg.mysqlhost.com`                        |
| port            | The port to use                                                                     | Optional                                                           | `3306`                                         |
| schema          | Specify the schema (database) to build models into                                  | Required                                                           | `analytics`                                    |
| username        | The username to use to connect to the server                                        | Required                                                           | `dbt_admin`                                    |
| password        | The password to use for authenticating to the server                                | Required                                                           | `correct-horse-battery-staple`                 |
| ssl_disabled    | Set to enable or disable TLS connectivity to mysql5.x                               | Optional                                                           | `True` or `False`                              |

### Notes

Conflicting terminology is used between:
- dbt
- Database management systems (DBMS) like MySQL, Postgres, and Snowflake
- metadata in the ANSI-standard `information_schema`

The conflicts include both:
- the same word meaning different things
- different words meaning the same thing

For example, a "database" in MySQL is not the same as a "database" in dbt, but it is equivalent to a "schema" in Postgres 🤯.

dbt-mysql uses the dbt terms. The native MySQL verbiage is restricted to SQL statements.

This cross-walk aligns the terminology:

| information_schema    | dbt (and Postgres)           | MySQL                            |
| --------------------- | ---------------------------- | -------------------------------- |
| catalog               |  database                    | _undefined / not implemented_    |
| schema                |  schema                      | database                         |
| relation (table/view) |  relation (table/view)       | relation (table/view)            |
| column                |  column                      | column                           |

Additionally, many DBMS have relation names with three parts whereas MySQL has only two. E.g., a fully-qualified table name in Postgres is `database.schema.table` versus `database.table` in MySQL. The missing part in MySQL is the `information_schema` "catalog".

| DBMS               | Fully-qualified relation name | Parts      |
| ------------------ | ----------------------------- | ---------- |
| Postgres           |  `database.schema.table`      | 3          |
| MySQL              |  `database.table`             | 2          |

### Running Tests

See [test/README.md](test/README.md) for details on running the integration tests.

### Reporting bugs and contributing code

-   Want to report a bug or request a feature? See the [contributing guidelines](https://github.com/dbeatty10/dbt-mysql/blob/main/CONTRIBUTING.rst#contributing), or open [an issue](https://github.com/dbeatty10/dbt-mysql/issues/new).

### Credits

dbt-mysql borrows from [dbt-spark](https://github.com/fishtown-analytics/dbt-spark) and [dbt-sqlite](https://github.com/codeforkjeff/dbt-sqlite) since Spark and SQLite also use two-part relation names.
