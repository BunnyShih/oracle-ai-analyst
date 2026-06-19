# Oracle Legacy → AI Analyst

> Extract data from legacy Oracle databases, enforce PII security, and generate bilingual AI-powered reports — in one command.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Claude API](https://img.shields.io/badge/Claude-API-orange) ![Security](https://img.shields.io/badge/PII-Masking-green)

---

## What This Does

Many enterprises run mission-critical data on Oracle systems built 10–20 years ago. Getting insight from that data typically means manual exports, spreadsheet work, and hours of analysis.

This project bridges the gap:

```
Legacy Oracle DB  →  ETL + PII Masking  →  Claude AI  →  Bilingual Report
```

One command produces a structured Markdown report in both English and Traditional Chinese, with zero PII ever leaving your security boundary.

---

## Architecture

```
oracle-ai-analyst/
├── mock_oracle/
│   └── data.py          # Simulates cx_Oracle — swap for real DB in production
├── etl/
│   ├── connector.py     # Connection, schema discovery, SQL whitelist
│   └── pii_masker.py    # Automatic PII detection + pseudonymisation + audit log
├── ai/
│   └── analyst.py       # Claude API integration, prompt engineering
├── output/              # Generated reports (Markdown)
└── main.py              # Entry point
```

### Security Design

| Layer | Mechanism |
|---|---|
| SQL Injection Prevention | Table whitelist — only `ALLOWED_TABLES` can be queried |
| PII Field Masking | Named field detection (NAME, EMAIL, PHONE, ID_NUMBER, CREDIT_CARD) |
| PII Value Scanning | Regex scan on all fields, even unlisted ones |
| Pseudonymisation | SHA-256 deterministic tokens — reversible only with original data |
| Audit Logging | Every query logged: timestamp, user, table, rows, PII fields masked |

No raw PII is ever sent to the Claude API.

---

## Quick Start

### 1. Clone & install
```bash
git clone https://github.com/yourname/oracle-ai-analyst
cd oracle-ai-analyst

# (recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 2. Run in demo mode (no API key needed)
```bash
python main.py
```

### 3. Run with live Claude AI analysis
```bash
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

### 4. Switch to real Oracle (production)
In `etl/connector.py`, replace:
```python
self.conn = MockConnection()
```
with:
```python
import cx_Oracle
self.conn = cx_Oracle.connect(user=user, password=password, dsn=dsn)
```

---

## Sample Output

```
[1/4] Connecting to Oracle (mock mode)...
      Schema discovered: ['SALES', 'CUSTOMERS']
[2/4] Extracting and masking SALES data...
      200 rows extracted, PII masked automatically.
[3/4] Security audit log:
      2026-06-17T12:00:00Z | table=SALES | rows=200 | pii_masked=400
[4/4] Sending to Claude AI for analysis...

✅  Report saved → output/report_20260617_120000.md
```

**Generated report includes:**
- Executive Summary (English + Traditional Chinese)
- Key metrics table
- Regional revenue breakdown
- Month-over-month trend commentary
- Risk flags
- Actionable recommendations

---

## Skills Demonstrated

| Skill | Implementation |
|---|---|
| **Legacy Data to AI** | Oracle schema discovery, ETL pipeline, mock/real DB abstraction |
| **AI Security & Sandbox** | PII masking, SQL whitelist, audit logging, zero raw data to API |
| **AI-Driven Productivity** | Manual analysis (hours) → automated report (seconds) |

---

## Extending This Project

- **Add more tables**: extend `ALLOWED_TABLES` in `connector.py`
- **Slack/Email delivery**: pipe `report` string to your notification layer
- **Scheduled runs**: wrap `main.py` in a cron job or Airflow DAG
- **Real Oracle**: install `cx_Oracle` or `python-oracledb`, update connector

---

## License

MIT
