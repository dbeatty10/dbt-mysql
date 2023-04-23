import pytest
from dbt.tests.util import run_dbt, check_relations_equal, relation_from_name

schema_base_yml = """
version: 2
sources:
  - name: raw
    schema: "{{ target.schema }}"
    tables:
      - name: seed
        identifier: "{{ var('seed_name', 'base') }}"
"""

seeds_base_csv = """
actor_id,film_id,some_date
1,1,1981-05-20T06:46:51
2,1,1978-09-03T18:10:33
3,1,1982-03-11T03:59:51
4,1,1976-05-06T20:21:35
5,1,1976-06-06T14:53:12
1,2,1982-06-23T05:41:26
2,2,1991-08-10T23:12:21
3,2,1971-03-29T14:58:02
1,3,1988-02-26T02:55:24
2,3,1994-02-09T13:14:23
""".lstrip()


seeds_added_csv = """
actor_id,film_id,some_date
1,5,2014-09-07T17:04:27
2,5,2000-02-04T11:48:30
3,5,2001-07-10T07:32:52
4,5,2002-11-24T03:22:28
5,5,2009-11-15T11:57:15
1,6,2005-04-09T03:50:11
2,6,2019-08-06T19:28:17
3,6,2014-03-01T11:50:41
4,6,2009-06-06T07:12:49
5,6,2003-12-05T21:42:18
""".lstrip()

model_incremental = """
select * from {{ source('raw', 'seed') }}
""".strip()

cfg_mat_inc_comp_unq_key = """
  {{ config(materialized="incremental", unique_key=["actor_id", "film_id"]) }}
"""

cfg_mat_inc_sgl_unq_key = """
  {{ config(materialized="incremental", unique_key="'actor_id'") }}
"""


inc_single_sql = cfg_mat_inc_sgl_unq_key + model_incremental
inc_composite_sql = cfg_mat_inc_comp_unq_key + model_incremental


class BaseIncrementalCompositeUniqueKey:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"name": "incremental_with_composite_unique_key"}

    @pytest.fixture(scope="class")
    def models(self):
        return {"incremental_with_composite.sql": inc_composite_sql,
                "schema.yml": schema_base_yml}

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"base.csv": seeds_base_csv, "added.csv": seeds_added_csv}

    def test_incremental_with_composite_key(self, project):
        # seed command
        results = run_dbt(["seed"])
        assert len(results) == 2

        # base table rowcount
        relation = relation_from_name(project.adapter, "base")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 10

        # added table rowcount
        relation = relation_from_name(project.adapter, "added")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 10

        # run command
        # the "seed_name" var changes the seed identifier in the schema file
        results = run_dbt(["run", "--vars", "seed_name: base"])
        assert len(results) == 1

        # check relations equal
        check_relations_equal(project.adapter,
                              ["base", "incremental_with_composite"])

        # change seed_name var
        # the "seed_name" var changes the seed identifier in the schema file
        results = run_dbt(["run", "--vars", "seed_name: added"])
        assert len(results) == 1

        # check relations equal
        # check_relations_equal(project.adapter, ["added", "incremental"])

        relation = relation_from_name(project.adapter,
                                      "incremental_with_composite")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 20

        # re-add the same data
        results = run_dbt(["run", "--vars", "seed_name: added"])
        assert len(results) == 1

        relation = relation_from_name(project.adapter,
                                      "incremental_with_composite")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 20

        # get catalog from docs generate
        catalog = run_dbt(["docs", "generate"])
        assert len(catalog.nodes) == 3
        assert len(catalog.sources) == 1


class BaseIncrementalSingleUniqueKey:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"name": "incremental_with_single_unique_key"}

    @pytest.fixture(scope="class")
    def models(self):
        return {"incremental_with_single.sql": inc_composite_sql,
                "schema.yml": schema_base_yml}

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"base.csv": seeds_base_csv, "added.csv": seeds_added_csv}

    def test_incremental_with_single_key(self, project):
        # seed command
        results = run_dbt(["seed"])
        assert len(results) == 2

        # base table rowcount
        relation = relation_from_name(project.adapter, "base")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 10

        # added table rowcount
        relation = relation_from_name(project.adapter, "added")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 10

        # run command
        # the "seed_name" var changes the seed identifier in the schema file
        results = run_dbt(["run", "--vars", "seed_name: base"])
        assert len(results) == 1

        # check relations equal
        check_relations_equal(project.adapter,
                              ["base", "incremental_with_single"])

        # change seed_name var
        # the "seed_name" var changes the seed identifier in the schema file
        results = run_dbt(["run", "--vars", "seed_name: added"])
        assert len(results) == 1

        # check relations equal
        # check_relations_equal(project.adapter, ["added", "incremental"])

        relation = relation_from_name(project.adapter,
                                      "incremental_with_single")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 20

        # re-add the same data
        results = run_dbt(["run", "--vars", "seed_name: added"])
        assert len(results) == 1

        relation = relation_from_name(project.adapter,
                                      "incremental_with_single")
        result = project.run_sql(
            f"select count(*) as num_rows from {relation}",
            fetch="one")
        assert result[0] == 20

        # get catalog from docs generate
        catalog = run_dbt(["docs", "generate"])
        assert len(catalog.nodes) == 3
        assert len(catalog.sources) == 1
