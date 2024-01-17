from dataclasses import dataclass, field

from dbt.adapters.base.relation import BaseRelation, Policy
from dbt.exceptions import DbtRuntimeError


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
    quote_policy: MariaDBQuotePolicy = field(default_factory=lambda: MariaDBQuotePolicy())
    include_policy: MariaDBIncludePolicy = field(default_factory=lambda: MariaDBIncludePolicy())
    quote_character: str = "`"

    def __post_init__(self):
        if self.database != self.schema and self.database:
            raise DbtRuntimeError(
                f"Cannot set `database` to '{self.database}' in MariaDB!"
                "You can either unset `database`, or make it match `schema`, "
                f"currently set to '{self.schema}'"
            )

    def render(self):
        if self.include_policy.database and self.include_policy.schema:
            raise DbtRuntimeError(
                "Got a MariaDB relation with schema and database set to "
                "include, but only one can be set"
            )
        return super().render()
