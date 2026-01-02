from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import get_supabase_admin_client


def main() -> None:
    sb = get_supabase_admin_client()
    rows = sb.select(
        "fundamentals_raw",
        "select=ticker,as_of_date,source,payload&order=created_at.desc&limit=1",
    )
    if not rows:
        print("No rows")
        return

    row = rows[0]
    payload = row.get("payload") or {}
    print(f"ticker={row.get('ticker')} as_of_date={row.get('as_of_date')} source={row.get('source')}")
    if isinstance(payload, dict):
        keys = sorted(payload.keys())
        print(f"Top-level keys: {len(keys)}")
        sample = keys[:40]
        if sample:
            print("Sample:")
            print("  " + ", ".join(sample) + (" ..." if len(keys) > len(sample) else ""))

        # Print a few likely fundamentals fields if present
        likely = [
            "regularMarketPrice",
            "marketCap",
            "trailingPE",
            "priceToBook",
            "dividendYield",
            "trailingAnnualDividendYield",
            "trailingAnnualDividendRate",
            "epsTrailingTwelveMonths",
            "earningsPerShare",
            "returnOnEquity",
            "roe",
        ]
        found = {k: payload.get(k) for k in likely if k in payload}
        if found:
            print("\nLikely fields found:")
            print(json.dumps(found, indent=2, ensure_ascii=False))
        else:
            print("\nNo likely fundamentals fields found at top-level.")

        # Print nested summaries (only if present)
        for nested_key in ["summaryProfile", "defaultKeyStatistics", "financialData", "summaryDetail"]:
            if nested_key in payload and isinstance(payload[nested_key], dict):
                nested_keys = sorted(payload[nested_key].keys())
                print(f"\nNested: {nested_key} keys: {len(nested_keys)}")
                n_sample = nested_keys[:30]
                if n_sample:
                    print("  " + ", ".join(n_sample) + (" ..." if len(nested_keys) > len(n_sample) else ""))
    else:
        print(f"Payload is not dict: {type(payload)}")


if __name__ == "__main__":
    main()
