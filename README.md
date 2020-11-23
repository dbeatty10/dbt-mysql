# dbt-mysql

This plugin ports [dbt](https://getdbt.com) functionality to MySQL 8.0.

This is an experimental plugin. Please read these docs carefully and use at your own risk. Issues and PRs welcome!

### Untested

We have not tested it against older versions of MySQL or storage engines other than the default of InnoDB.

Compatiblity with other [dbt packages](https://hub.getdbt.com/) (like [dbt_utils](https://hub.getdbt.com/fishtown-analytics/dbt_utils/latest/)) is also untested.

### Installation
This plugin can be installed via pip:

```bash
# Install dbt-mysql from PyPi:
$ pip install dbt-mysql
```

dbt-mysql creates connections via an ODBC driver that requires [`pyodbc`](https://github.com/mkleehammer/pyodbc).

See https://github.com/mkleehammer/pyodbc/wiki/Install for more info about installing `pyodbc`.

### Supported features

| Supported?      | Feature                           |
| --------------- | --------------------------------- |
| ✅              | Table materialization             |
| ✅              | View materialization              |
| ✅              | Incremental materialization       |
| ✅              | Ephemeral materialization         |
| ✅              | Seeds                             |
| ✅              | Sources                           |
| ✅              | Custom data tests                 |
| ✅              | Docs generate                     |
| ✅              | Snapshots                         |

### Configuring your profile

A dbt profile can be configured to run against MySQL using the following configuration:

| Option          | Description                                                                         | Required?                                                          | Example                                        |
| --------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| schema          | Specify the schema (database) to build models into                                  | Required                                                           | `analytics`                                    |
| server          | The server (hostname) to connect to                                                 | Required                                                           | `yourorg.mysqlhost.com`                        |
| username        | The username to use to connect to the server                                        | Required                                                           | `dbt_admin`                                    |
| password        | The password to use for authenticating to the server                                | Required                                                           | `correct-horse-battery-staple`                 |
| driver          | ODBC DSN configured                                                                 | Required                                                           | `MySQL ODBC 8.0 ANSI Driver`                   |

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

### Notes
MySQL also has two-part relation names (similar to SQLite and Spark) whereas many database management systems have three-part relation names.

MySQL, dbt, and the ANSI-standard `information_schema` use different terminology for analagous concepts. Note that MySQL does not implement the top-level concept of the information_schema "catalog" (which dbt calls a "database").

This adapter handles the two-part relation names in MySQL similarly to the [dbt-spark](https://github.com/fishtown-analytics/dbt-spark) and [dbt-sqlite](https://github.com/codeforkjeff/dbt-sqlite) adapters.

This is as a cross-walk between each concept:

| information_schema | MySQL                            | dbt                          |
| ------------------ | -------------------------------- | ---------------------------- |
| catalog            | _undefined / not implemented_    |  database                    |
| schema             | database                         |  schema                      |
| table/view         | table/view                       |  relation                    |
| column             | column                           |  column                      |

### Running Tests

1. Modify `test/mysql.dbtspec` with your `server`, `username`, and `password`
1. Install the `pytest-dbt-adapter` package
1. Run the test specs in this repository

```
pip install pytest-dbt-adapter

pytest test/mysql.dbtspec
```

### Reporting bugs and contributing code

-   Want to report a bug or request a feature? See the [contributing guidelines](https://github.com/dbeatty10/dbt-mysql/blob/main/CONTRIBUTING.rst#contributing), or open [an issue](https://github.com/dbeatty10/dbt-mysql/issues/new).
