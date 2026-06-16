#!/usr/bin/env python3
"""Smoke-test Phase 7 and Phase 8 after Render deploy.

Usage:
  python smoke_test.py --phase7 https://rrs-phase7.onrender.com --phase8 https://rrs-phase8.onrender.com
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def get(url: str, headers: dict | None = None) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def post(url: str, payload: dict, headers: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode()
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test RRS Render backends")
    parser.add_argument("--phase7", required=True, help="Phase 7 base URL")
    parser.add_argument("--phase8", required=True, help="Phase 8 base URL")
    parser.add_argument("--api-key", default="phase7-demo-key", help="Bearer API key")
    args = parser.parse_args()

    p7 = args.phase7.rstrip("/")
    p8 = args.phase8.rstrip("/")
    auth = {"Authorization": f"Bearer {args.api_key}"}
    failed = 0

    print("== Phase 7 health ==")
    code, body = get(f"{p7}/v1/health")
    print(code, body)
    if code != 200:
        failed += 1

    print("\n== Phase 8 health ==")
    code, body = get(f"{p8}/api/v1/health")
    print(code, body)
    if code != 200:
        failed += 1

    print("\n== Phase 8 locations ==")
    code, body = get(f"{p8}/api/v1/locations", auth)
    print(code, f"count={body.get('count') if isinstance(body, dict) else body}")
    if code != 200:
        failed += 1

    print("\n== Phase 8 cuisines ==")
    code, body = get(f"{p8}/api/v1/cuisines", auth)
    print(code, f"count={body.get('count') if isinstance(body, dict) else body}")
    if code != 200:
        failed += 1

    print("\n== Phase 8 recommendations (via Phase 7) ==")
    code, body = post(
        f"{p8}/api/v1/recommendations",
        {
            "location": "bangalore",
            "budget": "medium",
            "cuisine": "north indian",
            "minRating": 4.0,
            "topK": 3,
            "userId": "smoke-test",
        },
        auth,
    )
    if isinstance(body, dict):
        print(code, f"recommendations={len(body.get('recommendations', []))}")
    else:
        print(code, body[:500] if isinstance(body, str) else body)
    if code != 200:
        failed += 1

    if failed:
        print(f"\n{failed} check(s) failed.", file=sys.stderr)
        return 1
    print("\nAll smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
