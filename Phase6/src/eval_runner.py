from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import requests


def load_benchmark(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_query(base_url: str, query: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{base_url}/recommendations"
    payload = {
        "location": query["location"],
        "budget": query["budget"],
        "cuisine": query["cuisine"],
        "minRating": query["minRating"],
        "tags": query.get("tags", []),
        "topK": query["topK"],
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def evaluate_relevance(response: Dict[str, Any], expected_location: str) -> Dict[str, Any]:
    recommendations = response.get("recommendations", [])
    if not recommendations:
        return {"precision": 0.0, "matched": 0, "total": 0, "avg_rating": 0.0}

    matched = 0
    ratings = []
    for rec in recommendations:
        # Check if restaurant location roughly matches expected location
        # The candidate location is embedded in the restaurantId as name::location
        rid = rec.get("restaurantId", "").lower()
        if expected_location.lower() in rid:
            matched += 1
        ratings.append(rec.get("rating", 0))

    precision = matched / len(recommendations)
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    return {
        "precision": round(precision, 4),
        "matched": matched,
        "total": len(recommendations),
        "avg_rating": round(avg_rating, 2),
    }


def run_evaluation(base_url: str = "http://localhost:8000", benchmark_path: Path | None = None) -> Dict[str, Any]:
    if benchmark_path is None:
        benchmark_path = Path(__file__).with_name("benchmark_queries.json")

    queries = load_benchmark(benchmark_path)
    results: List[Dict[str, Any]] = []
    total_latency = 0
    fallback_count = 0
    error_count = 0

    print(f"Running offline evaluation with {len(queries)} benchmark queries...")
    print("-" * 60)

    for i, query in enumerate(queries, 1):
        name = query["name"]
        print(f"[{i}/{len(queries)}] {name} ... ", end="", flush=True)
        try:
            t0 = time.time()
            response = run_query(base_url, query)
            latency_ms = int((time.time() - t0) * 1000)
            total_latency += latency_ms

            if response.get("usedFallback"):
                fallback_count += 1

            relevance = evaluate_relevance(response, query["expected_location"])
            result = {
                "name": name,
                "status": "ok",
                "latency_ms": latency_ms,
                "used_fallback": response.get("usedFallback", False),
                "recommendation_count": len(response.get("recommendations", [])),
                "relevance": relevance,
            }
            print(f"OK  ({latency_ms}ms, fallback={response.get('usedFallback', False)}, precision={relevance['precision']})")
        except Exception as exc:
            error_count += 1
            result = {
                "name": name,
                "status": "error",
                "error": str(exc),
            }
            print(f"ERROR ({exc})")

        results.append(result)

    summary = {
        "total_queries": len(queries),
        "successful": len([r for r in results if r["status"] == "ok"]),
        "errors": error_count,
        "fallback_count": fallback_count,
        "fallback_rate": round(fallback_count / max(len(queries), 1), 4),
        "avg_latency_ms": round(total_latency / max(len(queries), 1), 2),
        "avg_precision": round(
            sum(r["relevance"]["precision"] for r in results if r["status"] == "ok") / max(len([r for r in results if r["status"] == "ok"]), 1), 4
        ),
        "avg_rating": round(
            sum(r["relevance"]["avg_rating"] for r in results if r["status"] == "ok") / max(len([r for r in results if r["status"] == "ok"]), 1), 2
        ),
    }

    print("-" * 60)
    print(f"Summary: {summary['successful']}/{summary['total_queries']} passed")
    print(f"  Fallback rate: {summary['fallback_rate']:.2%}")
    print(f"  Avg latency:   {summary['avg_latency_ms']}ms")
    print(f"  Avg precision: {summary['avg_precision']:.2%}")
    print(f"  Avg rating:    {summary['avg_rating']}")

    return {
        "summary": summary,
        "results": results,
    }


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    benchmark_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    report = run_evaluation(base_url, benchmark_path)

    output_path = Path("eval_report.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nDetailed report saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
