"""
PII Masking Layer — Security Module
Automatically detects and masks Personally Identifiable Information
before any data is sent to external AI APIs.

Covered fields: names, emails, phone numbers, ID numbers, credit cards.
"""

import re
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Fields that must always be masked (whitelist approach)
PII_FIELD_NAMES = {
    "CUSTOMER_NAME", "NAME", "EMAIL", "PHONE",
    "ID_NUMBER", "CREDIT_CARD", "SSN", "PASSPORT",
}

# Regex patterns for value-level PII detection
PII_PATTERNS = {
    "email":       re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone":       re.compile(r"\+?\d[\d\s\-]{7,}\d"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "id_number":   re.compile(r"\b[A-Z]\d{9,}\b"),
}

AUDIT_LOG: list[dict] = []

def _pseudo(value: str) -> str:
    """Deterministic pseudonymisation — same input always gives same token."""
    h = hashlib.sha256(str(value).encode()).hexdigest()[:8].upper()
    return f"[MASKED-{h}]"

def mask_row(row: dict) -> dict:
    """
    Mask a single data row.
    Returns a new dict; never mutates the original.
    """
    masked = {}
    for field, value in row.items():
        str_val = str(value)
        if field.upper() in PII_FIELD_NAMES:
            masked[field] = _pseudo(str_val)
        else:
            # Value-level scan even for unlisted fields
            detected = False
            for ptype, pattern in PII_PATTERNS.items():
                if pattern.search(str_val):
                    masked[field] = _pseudo(str_val)
                    detected = True
                    break
            if not detected:
                masked[field] = value
    return masked

def mask_dataset(rows: list[dict], table: str, query_user: str = "system") -> list[dict]:
    """
    Mask a list of rows and write an audit log entry.
    """
    result = [mask_row(r) for r in rows]
    pii_count = sum(
        1 for row in rows for field in row
        if field.upper() in PII_FIELD_NAMES
    )
    _audit(table=table, rows=len(rows), pii_fields_masked=pii_count, user=query_user)
    return result

def _audit(table: str, rows: int, pii_fields_masked: int, user: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user,
        "table": table,
        "rows_processed": rows,
        "pii_fields_masked": pii_fields_masked,
    }
    AUDIT_LOG.append(entry)
    logger.info("AUDIT | %s", entry)

def get_audit_log() -> list[dict]:
    return list(AUDIT_LOG)
