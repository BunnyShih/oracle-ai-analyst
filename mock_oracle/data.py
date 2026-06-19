"""
Mock Oracle Database — simulates cx_Oracle interface.
In a real deployment, replace MockConnection with:
    import cx_Oracle
    conn = cx_Oracle.connect(user, password, dsn)
"""

import random
from datetime import datetime, timedelta

MOCK_SCHEMA = {
    "SALES": ["ORDER_ID", "CUSTOMER_ID", "CUSTOMER_NAME", "ID_NUMBER", "AMOUNT", "REGION", "ORDER_DATE", "STATUS"],
    "CUSTOMERS": ["CUSTOMER_ID", "NAME", "EMAIL", "PHONE", "CREDIT_CARD", "TIER"],
}

PII_FIELDS = {"CUSTOMER_NAME", "ID_NUMBER", "EMAIL", "PHONE", "CREDIT_CARD", "NAME"}

REGIONS = ["APAC", "EMEA", "AMER", "LATAM"]
STATUSES = ["COMPLETED", "PENDING", "CANCELLED", "REFUNDED"]
TIERS = ["GOLD", "SILVER", "BRONZE"]

def _random_date(days_back=60):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime("%Y-%m-%d")

def _mock_sales_row(i):
    return {
        "ORDER_ID": f"ORD-{10000+i}",
        "CUSTOMER_ID": f"C{random.randint(100,199)}",
        "CUSTOMER_NAME": random.choice(["Alice Chen", "Bob Smith", "Carol Wu", "David Lee"]),
        "ID_NUMBER": f"A{random.randint(100000000,999999999)}",
        "AMOUNT": round(random.uniform(500, 50000), 2),
        "REGION": random.choice(REGIONS),
        "ORDER_DATE": _random_date(),
        "STATUS": random.choice(STATUSES),
    }

def _mock_customer_row(i):
    return {
        "CUSTOMER_ID": f"C{100+i}",
        "NAME": random.choice(["Alice Chen", "Bob Smith", "Carol Wu", "David Lee"]),
        "EMAIL": f"user{i}@company.com",
        "PHONE": f"+886-9{random.randint(10000000,99999999)}",
        "CREDIT_CARD": f"4{'*'*12}{random.randint(1000,9999)}",
        "TIER": random.choice(TIERS),
    }

class MockCursor:
    def __init__(self, table, limit):
        self.table = table
        self.limit = limit
        self._rows = None
        self.description = [(col,) for col in MOCK_SCHEMA.get(table, [])]

    def execute(self, sql, params=None):
        if "SALES" in sql.upper():
            self._rows = [_mock_sales_row(i) for i in range(self.limit)]
        elif "CUSTOMERS" in sql.upper():
            self._rows = [_mock_customer_row(i) for i in range(self.limit)]
        else:
            self._rows = []

    def fetchall(self):
        return [list(row.values()) for row in self._rows]

    def fetchmany(self, n):
        return self.fetchall()[:n]

class MockConnection:
    """Drop-in mock for cx_Oracle.connect()"""
    def cursor(self):
        return None  # replaced in connector.py

    def close(self):
        pass

def get_mock_connection():
    return MockConnection()
