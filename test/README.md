# Testing dbt-mysql

## Overview

Here are the steps to run the integration tests:
1. Install the pytest-dbt-adapter package
1. Set environment variables
1. Run Docker containers (optional)
1. Run tests

## Simple example

Assuming the applicable `pytest-dbt-adapter` package is installed and environment variables are set:
```bash
pytest test/mysql.dbtspec
```

## Full example

### Install the pytest-dbt-adapter package

The official `pytest-dbt-adapter` package from Fishtown Analytics uses some SQL syntax not supported by MySQL.

This fork (and branch) contains the necessary changes: https://github.com/dbeatty10/dbt-adapter-tests/tree/dbt-mysql-0.19.0

#### Install via SSH

`pip install git+ssh://git@github.com/dbeatty10/dbt-adapter-tests.git@dbt-mysql-0.19.0#egg=pytest-dbt-adapter`

#### Install via HTTPS

`pip install git+https://github.com/dbeatty10/dbt-adapter-tests.git@dbt-mysql-0.19.0#egg=pytest-dbt-adapter`

### Environment variables

Create the following environment variables (e.g., `export {VARIABLE}={value}` in a bash shell or via a tool like [`direnv`](https://direnv.net/)):
    * `DBT_MYSQL_SERVER_NAME`
    * `DBT_MYSQL_USERNAME`
    * `DBT_MYSQL_PASSWORD`

### Docker

[Here](https://medium.com/@crmcmullen/how-to-run-mysql-in-a-docker-container-on-macos-with-persistent-local-data-58b89aec496a) is one guide on "How to Run MySQL in a Docker Container on macOS with Persistent Local Data".

In the docker commands below, the default MySQL username is `root` and the default server name is `localhost`. If they are used unaltered, then you should set the following environment variable values:
```
DBT_MYSQL_SERVER_NAME=localhost
DBT_MYSQL_USERNAME=root
```

If you use any bash special characters in your password (like `$`), then you will need to escape them (like `DBT_MYSQL_PASSWORD=pas\$word` instead of `DBT_MYSQL_PASSWORD=pas$word`).

#### MySQL 8.0
`docker run --name mysql8.0 --net dev-network -v /Users/YOUR_USERNAME/Develop/mysql_data/8.0:/var/lib/mysql -p 3306:3306 -d -e MYSQL_ROOT_PASSWORD=$DBT_MYSQL_PASSWORD mysql:8.0`

#### MySQL 5.6

Contents of `/Users/YOUR_USERNAME/Develop/mysql_data/5.6/my.cnf`:
```
[mysqld]
explicit_defaults_for_timestamp = true
```

`docker run --name mysql5.6 --net dev-network -v /Users/YOUR_USERNAME/Develop/mysql_data/5.6:/var/lib/mysql -v /Users/YOUR_USERNAME/Develop/mysql_data/5.6/my.cnf:/etc/my.cnf -p 3308:3306 -d -e MYSQL_ROOT_PASSWORD=$DBT_MYSQL_PASSWORD mysql:5.6`

#### MySQL 5.7

Contents of `/Users/YOUR_USERNAME/Develop/mysql_data/5.7/my.cnf`:
```
[mysqld]
explicit_defaults_for_timestamp = true
sql_mode = "ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,ALLOW_INVALID_DATES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION"
```

`docker run --name mysql5.7 --net dev-network -v /Users/YOUR_USERNAME/Develop/mysql_data/5.7:/var/lib/mysql -v /Users/YOUR_USERNAME/Develop/mysql_data/5.7/my.cnf:/etc/my.cnf -p 3307:3306 -d -e MYSQL_ROOT_PASSWORD=$DBT_MYSQL_PASSWORD mysql:5.7`

### Run tests

Run the test specs in this repository:
```
pytest -v test/integration/mysql-5.6.dbtspec && \
pytest -v test/integration/mysql-5.7.dbtspec && \
pytest -v test/integration/mysql-8.0.dbtspec
```
