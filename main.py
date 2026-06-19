#!/usr/bin/env python3
"""
Oracle Legacy to AI Analyst
============================
Main entry point. Run:
    python main.py

Set your API key via environment variable:
    export ANTHROPIC_API_KEY=sk-ant-...

Or it will use demo mode (mock report).
"""

import os
import json
from etl.connector import OracleConnector
from etl.pii_masker import get_audit_log
from ai.analyst import run_analysis, save_report

BANNER = """
╔══════════════════════════════════════════════╗
║      Oracle Legacy → AI Analyst  v1.0       ║
║  Legacy Data  │  PII Security  │  Claude AI  ║
╚══════════════════════════════════════════════╝
"""

def main():
    print(BANNER)

    # 1. Connect & extract
    print("[1/4] Connecting to Oracle (mock mode)...")
    db = OracleConnector()
    schema = db.get_schema()
    print(f"      Schema discovered: {list(schema.keys())}")

    print("[2/4] Extracting and masking SALES data...")
    sales = db.query("SALES", limit=200)
    print(f"      {len(sales)} rows extracted, PII masked automatically.")

    # 2. Show audit log
    print("[3/4] Security audit log:")
    for entry in get_audit_log():
        print(f"      {entry['timestamp']} | table={entry['table']} | "
              f"rows={entry['rows_processed']} | pii_masked={entry['pii_fields_masked']}")

    # 3. AI analysis
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    print("[4/4] Sending to Claude AI for analysis...")

    if not api_key:
        print("\n⚠️  No ANTHROPIC_API_KEY set — using demo report.\n")
        report = _demo_report(sales)
    else:
        report = run_analysis(sales, schema, api_key)

    # 4. Save & print
    path = save_report(report, output_dir="output")
    print(f"\n✅  Report saved → {path}\n")
    print("=" * 60)
    print(report)
    print("=" * 60)
    db.close()

def _demo_report(sales: list[dict]) -> str:
    total = len(sales)
    revenue = sum(float(r.get("AMOUNT", 0)) for r in sales)
    completed = sum(1 for r in sales if r.get("STATUS") == "COMPLETED")
    regions = {}
    for r in sales:
        reg = r.get("REGION", "UNKNOWN")
        regions[reg] = regions.get(reg, 0) + float(r.get("AMOUNT", 0))
    top_region = max(regions, key=regions.get)

    return f"""# Oracle Sales Analysis Report
*(Demo mode — set ANTHROPIC_API_KEY for live AI analysis)*

## Executive Summary (English)
Analysis of {total} orders extracted from the legacy Oracle SALES table shows total revenue of 
**${revenue:,.2f}**. The completion rate stands at **{completed/total*100:.1f}%**.
{top_region} leads all regions by revenue. PII masking was applied to all sensitive fields 
prior to this analysis, ensuring zero data exposure to external APIs.

## 執行摘要（繁體中文）
本次分析共涵蓋 {total} 筆訂單，總營收為 **${revenue:,.2f}**。
完成率為 **{completed/total*100:.1f}%**。{top_region} 地區營收最高。
所有個人識別資料（PII）均在傳送至 AI 前完成遮蔽，確保資料安全。

## Key Metrics
| Metric | Value |
|---|---|
| Total Orders | {total} |
| Total Revenue | ${revenue:,.2f} |
| Completion Rate | {completed/total*100:.1f}% |
| Top Region | {top_region} |

## Regional Breakdown
{chr(10).join(f"| {r} | ${v:,.2f} |" for r, v in sorted(regions.items(), key=lambda x: -x[1]))}

## Risk Flags
- Monitor cancellation/refund rate — target below 15%
- Review underperforming regions for pipeline gaps

## Recommendations
- Prioritise {top_region} expansion given strong revenue performance
- Automate weekly Oracle → AI reporting to reduce manual analysis time
- Enforce PII masking policy across all downstream integrations
"""

if __name__ == "__main__":
    main()
