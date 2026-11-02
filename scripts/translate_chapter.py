"""
Tech-Hinglish Translation Utility for System Design Notes.
Maintains technical terms in English while rendering concepts in clear, intuitive Hindi.
"""

import sys
import re
from pathlib import Path

# Common glossary of technical terms to strictly preserve in English
PROTECTED_TERMS = [
    "Latency", "Throughput", "Consistent Hashing", "Token Bucket",
    "Read-Heavy", "Write-Heavy", "Replication Lag", "Failover",
    "Load Balancer", "Single Point of Failure", "SPOF", "Cache Aside",
    "SSTable", "MemTable", "Bloom Filter", "Idempotency Key",
    "Double-Entry Ledger", "Quorum", "Vector Clock", "Snowflake ID",
    "Base62", "DNS", "CDN", "API Gateway", "Heartbeat", "Gossip Protocol"
]

def format_hinglish_summary(chapter_num: int, title: str, points: list[str]) -> str:
    out = [f"## Quick Interview Summary: {title}", ""]
    for p in points:
        out.append(f"- {p}")
    out.append("")
    return "\n".join(out)

if __name__ == "__main__":
    print(f"Loaded {len(PROTECTED_TERMS)} protected tech terms for Tech-Hinglish pipeline.")
