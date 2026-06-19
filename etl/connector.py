"""
Oracle Connector — ETL Layer
Handles connection, schema discovery, and data extraction.

To switch from mock to real Oracle:
    1. pip install cx_Oracle
    2. Replace get_connection() with cx_Oracle.connect(user, password, dsn)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mock_oracle.data import MockConnection, MockCursor, MOCK_SCHEMA
from etl.pii_masker import mask_dataset

ALLOWED_TABLES = {"SALES", "CUSTOMERS"}  # SQL whitelist — security layer

class OracleConnector:
    def __init__(self, user="demo", password="demo", dsn="mock"):
        self.user = user
        self.conn = MockConnection()  # swap with cx_Oracle.connect() for real DB

    def get_schema(self) -> dict:
        """Return table → column list mapping."""
        return {t: cols for t, cols in MOCK_SCHEMA.items() if t in ALLOWED_TABLES}

    def query(self, table: str, limit: int = 100) -> list[dict]:
        if table.upper() not in ALLOWED_TABLES:
            raise PermissionError(f"Table '{table}' is not in the allowed query whitelist.")

        cursor = MockCursor(table, limit)
        cursor.execute(f"SELECT * FROM {table} WHERE ROWNUM <= :lim", {"lim": limit})
        columns = [d[0] for d in cursor.description]
        rows_raw = cursor.fetchall()
        rows = [dict(zip(columns, row)) for row in rows_raw]

        # Pass through PII masking before returning
        masked = mask_dataset(rows, table=table, query_user=self.user)
        return masked

    def close(self):
        self.conn.close()
