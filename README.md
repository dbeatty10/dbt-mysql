# dbt-mysql

This plugin ports [dbt](https://getdbt.com) functionality to MySQL 8.0.

This is an experimental plugin:
- We have not tested it extensively or with storage engines other than the default of InnoDB
- MariaDB compatibility is untested
- Compatiblity with other [dbt packages](https://hub.getdbt.com/) (like [dbt_utils](https://hub.getdbt.com/fishtown-analytics/dbt_utils/latest/)) is also untested

Please read these docs carefully and use at your own risk. [Issues](https://github.com/dbeatty10/dbt-mysql/issues/new) and [PRs](https://github.com/dbeatty10/dbt-mysql/blob/main/CONTRIBUTING.rst#contributing) welcome!

### Installation
This plugin can be installed via pip:

```bash
$ pip install dbt-mysql
```

dbt-mysql creates connections via an ODBC driver that requires [`pyodbc`](https://github.com/mkleehammer/pyodbc).

See https://github.com/mkleehammer/pyodbc/wiki/Install for more info about installing `pyodbc`.

### Supported features for MySQL 8.0

| Supported? | Feature                           |
| ---------- | --------------------------------- |
| ✅         | Table materialization             |
| ✅         | View materialization              |
| ✅         | Incremental materialization       |
| ✅         | Ephemeral materialization         |
| ✅         | Seeds                             |
| ✅         | Sources                           |
| ✅         | Custom data tests                 |
| ✅         | Docs generate                     |
| ✅         | Snapshots                         |

### Supported features for MySQL 5.6 and 5.7

| Supported? | Feature                           |
| ---------- | --------------------------------- |
| ✅         | Table materialization             |
| ✅         | View materialization              |
| ✅         | Incremental materialization       |
| ❌         | Ephemeral materialization         |
| ✅         | Seeds                             |
| ✅         | Sources                           |
| ✅         | Custom data tests                 |
| ✅         | Docs generate                     |
| ✅         | Snapshots                         |

Ephemeral materializations rely upon Common Table Expressions (CTE), which is
not supported until MySQL 8.0

### Configuring your profile

A dbt profile can be configured to run against MySQL using the following configuration:

**Example entry for profiles.yml:**

```
your_profile_name:
  target: dev
  outputs:
    dev:
      type: mysql
      server: localhost
      schema: analytics
      username: your_mysql_username
      password: your_mysql_password
      driver: MySQL ODBC 8.0 ANSI Driver
```

| Option          | Description                                                                         | Required?                                                          | Example                                        |
| --------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| server          | The server (hostname) to connect to                                                 | Required                                                           | `yourorg.mysqlhost.com`                        |
| schema          | Specify the schema (database) to build models into                                  | Required                                                           | `analytics`                                    |
| username        | The username to use to connect to the server                                        | Required                                                           | `dbt_admin`                                    |
| password        | The password to use for authenticating to the server                                | Required                                                           | `correct-horse-battery-staple`                 |
| driver          | ODBC DSN configured                                                                 | Required                                                           | `MySQL ODBC 8.0 ANSI Driver`                   |

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


dbt-mysql borrows from [dbt-spark](https://github.com/fishtown-analytics/dbt-spark) and [dbt-sqlite](https://github.com/codeforkjeff/dbt-sqlite) since Spark and SQLite also use two-part relation names.

### Running Tests

1. Modify `test/mysql.dbtspec` with your `server`, `username`, and `password`
1. Install the `pytest-dbt-adapter` package
1. Run the test specs in this repository

```bash
$ pip install pytest-dbt-adapter
$ pytest test/mysql.dbtspec
```

### Reporting bugs and contributing code

-   Want to report a bug or request a feature? See the [contributing guidelines](https://github.com/dbeatty10/dbt-mysql/blob/main/CONTRIBUTING.rst#contributing), or open [an issue](https://github.com/dbeatty10/dbt-mysql/issues/new).
