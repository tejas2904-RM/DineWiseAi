from __future__ import annotations

import time
from typing import Any, Dict, List, Set, Tuple

from fallback import fallback_recommendations
from groq_adapter import GroqAdapter
from models import Candidate, Preference, RecommendationResponse
from parser import parse_recommendations
from prompt_builder import build_prompt


class Phase4Engine:
    def __init__(self, groq_adapter: GroqAdapter):
        self.groq_adapter = groq_adapter

    def generate(
        self, preference: Preference, candidates: List[Candidate], top_k: int
    ) -> Dict[str, Any]:
        telemetry: List[Dict[str, Any]] = []

        if not candidates:
            fb = fallback_recommendations(candidates=[], top_k=top_k)
            response = RecommendationResponse(
                recommendations=fb["recommendations"],
                summary=fb["summary"],
                used_fallback=True,
            ).__dict__
            response["fallback_reason"] = "no_candidates"
            response["llm_telemetry"] = telemetry
            return response

        candidate_ids: Set[str] = {c.restaurant_id for c in candidates}
        prompt = build_prompt(preference, candidates, top_k=top_k)

        # First attempt.
        try:
            t0 = time.time()
            llm_result = self.groq_adapter.generate(prompt)
            latency_ms = int((time.time() - t0) * 1000)
            telemetry.append(
                {
                    "attempt": 1,
                    "latency_ms": latency_ms,
                    "prompt_tokens": llm_result.get("prompt_tokens", 0),
                    "completion_tokens": llm_result.get("completion_tokens", 0),
                    "total_tokens": llm_result.get("total_tokens", 0),
                    "model": llm_result.get("model", ""),
                }
            )
            raw = llm_result["content"]
            parsed = parse_recommendations(raw, candidate_ids=candidate_ids, top_k=top_k)
            response = RecommendationResponse(
                recommendations=parsed["recommendations"],
                summary=parsed["summary"],
                used_fallback=False,
            ).__dict__
            response["fallback_reason"] = None
            response["llm_telemetry"] = telemetry
            return response
        except Exception as first_error:
            # Retry once with stricter instruction.
            retry_prompt = prompt + "\n\nIMPORTANT: Return only valid JSON. Do not include extra text."
            try:
                t0 = time.time()
                llm_result = self.groq_adapter.generate(retry_prompt)
                latency_ms = int((time.time() - t0) * 1000)
                telemetry.append(
                    {
                        "attempt": 2,
                        "latency_ms": latency_ms,
                        "prompt_tokens": llm_result.get("prompt_tokens", 0),
                        "completion_tokens": llm_result.get("completion_tokens", 0),
                        "total_tokens": llm_result.get("total_tokens", 0),
                        "model": llm_result.get("model", ""),
                    }
                )
                raw_retry = llm_result["content"]
                parsed_retry = parse_recommendations(raw_retry, candidate_ids=candidate_ids, top_k=top_k)
                response = RecommendationResponse(
                    recommendations=parsed_retry["recommendations"],
                    summary=parsed_retry["summary"],
                    used_fallback=False,
                ).__dict__
                response["fallback_reason"] = None
                response["llm_telemetry"] = telemetry
                return response
            except Exception as second_error:
                fb = fallback_recommendations(candidates=candidates, top_k=top_k)
                response = RecommendationResponse(
                    recommendations=fb["recommendations"],
                    summary=fb["summary"],
                    used_fallback=True,
                ).__dict__
                response["fallback_reason"] = (
                    f"first_attempt={type(first_error).__name__}: {first_error}; "
                    f"retry_attempt={type(second_error).__name__}: {second_error}"
                )
                response["llm_telemetry"] = telemetry
                return response
