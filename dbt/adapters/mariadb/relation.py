from dataclasses import dataclass

from dbt.adapters.base.relation import BaseRelation, Policy
from dbt.exceptions import RuntimeException


@dataclass
class MariaDBQuotePolicy(Policy):
    database: bool = False
    schema: bool = True
    identifier: bool = True


@dataclass
class MariaDBIncludePolicy(Policy):
    database: bool = False
    schema: bool = True
    identifier: bool = True


@dataclass(frozen=True, eq=False, repr=False)
class MariaDBRelation(BaseRelation):
    quote_policy: MariaDBQuotePolicy = MariaDBQuotePolicy()
    include_policy: MariaDBIncludePolicy = MariaDBIncludePolicy()
    quote_character: str = '`'

    def __post_init__(self):
        if self.database != self.schema and self.database:
            raise RuntimeException(f'Cannot set database {self.database} in MariaDB!')

    def render(self):
        if self.include_policy.database and self.include_policy.schema:
            raise RuntimeException(
                "Got a MariaDB relation with schema and database set to "
                "include, but only one can be set"
            )
        return super().render()
