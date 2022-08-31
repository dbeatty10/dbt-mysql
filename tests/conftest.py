import pytest
import os

# Import the fuctional fixtures as a plugin
# Note: fixtures with session scope need to be local

pytest_plugins = ["dbt.tests.fixtures.project"]

# The profile dictionary, used to write out profiles.yml
# dbt will supply a unique schema per test, so we do not specify 'schema' here
@pytest.fixture(scope="class")
def dbt_profile_target():
    return {
        "type": "mysql",
        "threads": 1,
        "host": os.getenv("DBT_MYSQL_SERVER_NAME", "127.0.0.1"),
        "user": os.getenv("DBT_MYSQL_USERNAME", "root"),
        "password": os.getenv("DBT_MYSQL_PASSWORD", ""),
        "port": os.getenv("DBT_MYSQL_PORT", 3306),
    }
