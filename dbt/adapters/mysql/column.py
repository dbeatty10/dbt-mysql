from dataclasses import dataclass
from typing import TypeVar, Optional, Dict, Any

from dbt.adapters.base.column import Column

Self = TypeVar("Self", bound="MySQLColumn")


@dataclass
class MySQLColumn(Column):
    TYPE_LABELS = {
        "STRING": "TEXT",
        "VAR_STRING": "TEXT",
        "LONG": "INTEGER",
        "LONGLONG": "INTEGER",
        "INT": "INTEGER",
        "TIMESTAMP": "DATETIME",
    }
    table_database: Optional[str] = None
    table_schema: Optional[str] = None
    table_name: Optional[str] = None
    table_type: Optional[str] = None
    table_owner: Optional[str] = None
    table_stats: Optional[Dict[str, Any]] = None
    column_index: Optional[int] = None

    @property
    def quoted(self) -> str:
        return "`{}`".format(self.column)

    def __repr__(self) -> str:
        return "<MySQLColumn {} ({})>".format(self.name, self.data_type)
