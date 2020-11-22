from dataclasses import dataclass

from dbt.adapters.base.relation import BaseRelation, Policy
from dbt.exceptions import RuntimeException

#----Remove when done troubleshooting
from dbt.contracts.relation import (
    RelationType, ComponentName, HasQuoting, FakeAPIObject, Policy, Path
)
from typing import (
    Optional
)
from dbt.utils import filter_null_values
#----Remove when done troubleshooting


@dataclass
class MySQLQuotePolicy(Policy):
    database: bool = False
    schema: bool = False
    identifier: bool = False


@dataclass
class MySQLIncludePolicy(Policy):
    database: bool = False
    schema: bool = True
    identifier: bool = True


@dataclass(frozen=True, eq=False, repr=False)
class MySQLRelation(BaseRelation):
    quote_policy: MySQLQuotePolicy = MySQLQuotePolicy()
    include_policy: MySQLIncludePolicy = MySQLIncludePolicy()
    quote_character: str = '`'

    def __post_init__(self):
        if self.database != self.schema and self.database:
            raise RuntimeException(f'Cannot set database {self.database} in mysql!')

    def render(self):
        if self.include_policy.database and self.include_policy.schema:
            raise RuntimeException(
                "Got a mysql relation with schema and database set to "
                "include, but only one can be set"
            )
        return super().render()

    def matches(
        self,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        identifier: Optional[str] = None,
    ) -> bool:
        search = filter_null_values({
            ComponentName.Database: database,
            ComponentName.Schema: schema,
            ComponentName.Identifier: identifier
        })

        if not search:
            # nothing was passed in
            raise dbt.exceptions.RuntimeException(
                "Tried to match relation, but no search path was passed!")

        exact_match = True
        approximate_match = True

        for k, v in search.items():
            if not self._is_exactish_match(k, v):
                exact_match = False

            if self.path.get_lowered_part(k) != v.lower():
                approximate_match = False

        if approximate_match and not exact_match:
            target = self.create(
                database=database, schema=schema, identifier=identifier
            )
            dbt.exceptions.approximate_relation_match(target, self)

        return exact_match
