from __future__ import annotations

import json
import os

from dotenv import load_dotenv

from integrations.hgbrasil_integration import HGBrasilIntegration


def _print_results(label: str, resp: dict) -> None:
    print(f"\n=== {label} ===")
    print("keys", list(resp.keys()))
    results = resp.get("results")
    print("results_type", type(results).__name__)
    if "errors" in resp:
        errs = resp.get("errors")
        print("errors_type", type(errs).__name__)
        if errs:
            print("errors_json", json.dumps(errs, ensure_ascii=False)[:600])
    if isinstance(results, dict):
        # HG costuma retornar {error: true, message: ...}
        if results.get("error") or results.get("error") is True or results.get("erro") is True:
            print("ERROR", results.get("message") or results.get("mensagem") or results)
        else:
            print("results_keys_sample", list(results.keys())[:20])
            print("results_json_prefix", json.dumps(results, ensure_ascii=False)[:600])
    else:
        print("results_json_prefix", json.dumps(results, ensure_ascii=False)[:600])


def main() -> None:
    load_dotenv(dotenv_path=".env.local", override=False)
    key = (os.getenv("HGBRASIL_KEY") or os.getenv("HG_BRASIL_KEY") or "").strip() or None
    print("has_key", bool(key))

    hg = HGBrasilIntegration(api_key=key)

    # 1) stock_price (finance)
    resp = hg.get_stock_price("itub4")
    _print_results("stock_price(itub4)", resp)

    # 2) v2 historical
    resp = hg.get_historical_v2("B3:ITUB4", days_ago=10)
    _print_results("v2 historical(B3:ITUB4, days_ago=10)", resp)

    # 3) v2 dividends
    resp = hg.get_dividends_v2("B3:ITUB4", days_ago=365)
    _print_results("v2 dividends(B3:ITUB4, days_ago=365)", resp)


if __name__ == "__main__":
    main()
