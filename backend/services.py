from sqlalchemy import text
from sqlalchemy.engine import Engine

class BaseSchemaManager:
    SYSTEM_COLUMNS = {"id", "product_id"}

    def __init__(self, engine: Engine, table_name: str):
        self.engine = engine
        self.table_name = table_name

    def get_existing_columns(self) -> set:
        with self.engine.connect() as conn:
            result = conn.execute(
                text(f"PRAGMA table_info({self.table_name})")
            )
            return {row[1] for row in result}

    def infer_sql_type(self, value):
        if isinstance(value, bool):
            return "INTEGER"
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"
        return "TEXT"

    def add_column(self, column_name: str, column_type: str):
        ddl = (
            f'ALTER TABLE {self.table_name} '
            f'ADD COLUMN "{column_name}" {column_type}'
        )
        with self.engine.connect() as conn:
            conn.execute(text(ddl))


class EUTSchemaManager(BaseSchemaManager):

    def ensure_columns_from_payload(self, payload: dict):
        existing_columns = self.get_existing_columns()

        for key, value in payload.items():
            if key in self.SYSTEM_COLUMNS:
                continue

            if key not in existing_columns:
                col_type = self.infer_sql_type(value)
                self.add_column(key, col_type)
