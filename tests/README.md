# Testing dbt-mysql

## Overview

Here are the steps to run the integration tests:
1. Set environment variables
1. Run Docker containers (optional)
1. Run tests

## Simple example

Assuming the applicable `dbt-tests-adapter` package is installed and environment variables are set:
```bash
PYTHONPATH=. pytest tests/functional/adapter/test_basic.py
```

## Full example

### Prerequisites

#### Dependencies

`pip install -r ./dev-requirements.txt`

#### Python Version

Python 3.8 and 3.9 are supported test targets and may need to be installed before tests can run.

##### Ubuntu

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.8 python3.8-distutils python3.9 python3.9-distutils
```

### Environment variables

Create the following environment variables (e.g., `export {VARIABLE}={value}` in a bash shell or via a tool like [`direnv`](https://direnv.net/)):
* `DBT_MYSQL_SERVER_NAME`
* `DBT_MYSQL_USERNAME`
* `DBT_MYSQL_PASSWORD`
* `DBT_MARIADB_105_PORT`
* `DBT_MYSQL_57_PORT`
* `DBT_MYSQL_80_PORT`

`.env.example` has a listing of environment variables and values. You can use it with Docker by configuring a `.env` file with appropriate variables:

```shell
cp .env.example .env
$EDITOR .env
```

By default, [Docker will automatically load environment variables](https://docs.docker.com/compose/env-file/) from a file named `.env`.

### Docker

#### Easiest

This command will launch local databases for testing:
```shell
docker-compose up -d
```

Skip to down below and follow the instructions to ["Run tests"](#run-tests).

When finished using the containers:
```shell
docker-compose down
```

#### Harder

<details>
  <summary>More complicated docker setup commands</summary>

[Here](https://medium.com/@crmcmullen/how-to-run-mysql-in-a-docker-container-on-macos-with-persistent-local-data-58b89aec496a) is one guide on "How to Run MySQL in a Docker Container on macOS with Persistent Local Data".

In the docker commands below, the default MySQL username is `root` and the default server name is `localhost`. If they are used unaltered, then you should set the following environment variable values:
```
DBT_MYSQL_SERVER_NAME=localhost
DBT_MYSQL_USERNAME=root
```

If you use any bash special characters in your password (like `$`), then you will need to escape them (like `DBT_MYSQL_PASSWORD=pas\$word` instead of `DBT_MYSQL_PASSWORD=pas$word`).

#### MySQL 8.0
`docker run --name mysql8.0 --net dev-network -v /Users/YOUR_USERNAME/Develop/mysql_data/8.0:/var/lib/mysql -p 3306:3306 -d -e MYSQL_ROOT_PASSWORD=$DBT_MYSQL_PASSWORD mysql:8.0`

#### MySQL 5.7

Contents of `/Users/YOUR_USERNAME/Develop/mysql_data/5.7/my.cnf`:
```
[mysqld]
explicit_defaults_for_timestamp = true
sql_mode = "ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,ALLOW_INVALID_DATES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION"
```

`docker run --name mysql5.7 --net dev-network -v /Users/YOUR_USERNAME/Develop/mysql_data/5.7:/var/lib/mysql -v /Users/YOUR_USERNAME/Develop/mysql_data/5.7/my.cnf:/etc/my.cnf -p 3307:3306 -d -e MYSQL_ROOT_PASSWORD=$DBT_MYSQL_PASSWORD mysql:5.7`

</details>

### Run tests

Run all the tests via `make`:
```shell
make unit
make integration
```

Or run all the tests via `tox`:
```shell
tox
```

Or run the test specs directly
```shell
PYTHONPATH=. pytest -v --profile mysql tests/functional && \
PYTHONPATH=. pytest -v --profile mysql5 tests/functional && \
PYTHONPATH=. pytest -v --profile mariadb tests/functional
```

Or run a single test
```shell
pytest -v --profile mysql tests/functional/adapter/test_basic.py::TestEmptyMySQL::test_empty
```
