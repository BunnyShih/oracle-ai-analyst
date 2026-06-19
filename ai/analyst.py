"""
AI Analyst — Claude API Integration
Sends masked data to Claude and returns a structured bilingual report.
"""

import os
import json
import requests
from datetime import datetime

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """You are an enterprise data analyst. 
You receive sanitized (PII-masked) sales data extracted from a legacy Oracle database.
Your job is to produce a concise bilingual (English + Traditional Chinese) analysis report in Markdown.

Structure your report exactly as:
# Oracle Sales Analysis Report

## Executive Summary (English)
3-5 sentences covering key findings.

## 執行摘要（繁體中文）
Same summary in Traditional Chinese.

## Key Metrics
- Total orders, total revenue, top region, completion rate

## Regional Breakdown
Table of region vs revenue vs order count.

## Month-over-Month Trend
Brief trend commentary based on ORDER_DATE distribution.

## Risk Flags
Any anomalies: high cancellation rate, regional underperformance, etc.

## Recommendations
2-3 actionable bullet points.

Be precise with numbers. Do not invent data not present in the input."""

def build_prompt(sales_data: list[dict], schema: dict) -> str:
    sample = sales_data[:50]  # stay within token budget
    return f"""Analyze the following Oracle SALES table extract.

Schema: {json.dumps(schema.get('SALES', []))}

Data ({len(sample)} rows of {len(sales_data)} total):
{json.dumps(sample, indent=2, default=str)}

Generate the bilingual analysis report now."""

def run_analysis(sales_data: list[dict], schema: dict, api_key: str) -> str:
    prompt = build_prompt(sales_data, schema)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 2000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }

    resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]

def save_report(report: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"report_{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path
