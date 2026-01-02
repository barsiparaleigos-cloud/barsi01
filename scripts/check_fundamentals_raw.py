from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import get_supabase_admin_client


def main() -> None:
    sb = get_supabase_admin_client()
    rows = sb.select(
        "fundamentals_raw",
        "select=ticker,as_of_date,source,created_at&order=created_at.desc&limit=5",
    )
    print(rows)


if __name__ == "__main__":
    main()
