from __future__ import annotations

import json
import os

from dotenv import load_dotenv

from integrations.hgbrasil_integration import HGBrasilIntegration


def main() -> None:
    load_dotenv(dotenv_path=".env.local", override=False)
    key = (os.getenv("HGBRASIL_KEY") or os.getenv("HG_BRASIL_KEY") or "").strip() or None
    print("has_key", bool(key))
    hg = HGBrasilIntegration(api_key=key)

    resp = hg.get_stock_price("ITUB4")
    print("resp_keys", list(resp.keys()))

    results = resp.get("results")
    print("results_type", type(results).__name__)

    payload = None
    if isinstance(results, dict):
        print("results_keys_sample", list(results.keys())[:15])
        payload = results.get("ITUB4")
        if not isinstance(payload, dict):
            payload = next((v for v in results.values() if isinstance(v, dict)), None)
    elif isinstance(results, list):
        payload = next((v for v in results if isinstance(v, dict)), None)

    print("payload_type", type(payload).__name__)
    if isinstance(payload, dict):
        print("payload_keys_sample", list(payload.keys())[:40])
        for k in [
            "price",
            "close",
            "regularMarketPrice",
            "change_percent",
            "volume",
            "updated_at",
            "symbol",
            "name",
            "company_name",
        ]:
            if k in payload:
                print(k, payload.get(k))
        print("payload_json_prefix", json.dumps(payload, ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
