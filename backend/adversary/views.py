"""
Adversary Views (v2.0) — RAG-Augmented Vulnerability Analysis
===============================================================
- RAG-powered vulnerability detection (shares the visualizer's ChromaDB engine)
- Persistent response caching via Django models
- Multi-layer heuristic fallback with pattern matching
- Analytics tracking for all attack analyses
- Proper serializer validation
"""

import logging
import os
import time
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AdversaryAnalysis, CachedAdversaryResult
from .serializers import AdversaryAttackRequestSerializer

from visualizer.llm_factory import get_llm_chain

logger = logging.getLogger(__name__)

# Cache chains per process
_chains = {}

def _get_cached_chain(api_key: str, app_type: str):
    key = f"{api_key[:10]}_{app_type}"
    if key not in _chains:
        _chains[key] = get_llm_chain(api_key, app_type)
    return _chains[key]



def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


class AdversaryAttackView(APIView):
    """
    POST /api/v1/adversary/attack/

    Performs adversarial vulnerability analysis on user code using RAG-augmented LLM.
    """

    def _get_active_api_key(self):
        """Find the first available and valid API key."""
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key.startswith("sk-") and "exhausted" not in openai_key:
            return openai_key
        
        google_key = os.getenv("GOOGLE_API_KEY", "")
        if google_key:
            return google_key
            
        return None

    def post(self, request):
        total_start = time.perf_counter()

        # ── 1. Validate Input ────────────────────────────────
        serializer = AdversaryAttackRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_code = serializer.validated_data["user_code"]
        problem_type = serializer.validated_data.get("problem_type", "General DSA")
        force_refresh = serializer.validated_data.get("force_refresh", False)
        code_hash = AdversaryAnalysis.compute_code_hash(user_code)
        client_ip = get_client_ip(request)

        # ── 2. Check Persistent Cache ────────────────────────
        if not force_refresh:
            cached = CachedAdversaryResult.get_or_none(code_hash, problem_type)
            if cached:
                total_ms = (time.perf_counter() - total_start) * 1000
                self._track_analysis(
                    code_hash, user_code, problem_type, "cached",
                    cached.response_json, total_ms, client_ip
                )
                response_data = cached.response_json.copy()
                response_data["cached"] = True
                response_data["latency_ms"] = round(total_ms, 2)
                return Response(response_data, status=status.HTTP_200_OK)

        # ── 3. Check for Active API Key ──────────────────────
        api_key = self._get_active_api_key()
        if not api_key:
            return self._heuristic_fallback(
                user_code, problem_type, code_hash, client_ip,
                total_start, "No valid API key in .env"
            )

        # ── 4. RAG Context Retrieval ─────────────────────────
        context = ""
        try:
            from visualizer.rag_engine import get_rag_engine
            rag_engine = get_rag_engine()
            context = rag_engine.get_context_string(
                user_code, k=3, use_mmr=True, collection_name="adversary_knowledge_v1"
            )
        except Exception as rag_err:
            logger.warning(f"Adversary RAG retrieval failed: {rag_err}")


        # ── 5. LLM Analysis ─────────────────────────────────
        try:
            chain = _get_cached_chain(api_key, "adversary")
            result = chain.invoke({
                "context": context,
                "problem_type": problem_type,
                "user_code": user_code,
            })

            total_ms = (time.perf_counter() - total_start) * 1000

            # Ensure all expected fields exist
            result.setdefault("adversary_feedback", "Analysis complete.")
            result.setdefault("edge_case_input", "[]")
            result.setdefault("injection_attempt_detected", False)
            result.setdefault("vulnerability_severity", "medium")
            result.setdefault("vulnerability_categories", [])
            result["rag_context_used"] = bool(context)
            result["latency_ms"] = round(total_ms, 2)

            # ── 6. Cache & Track ─────────────────────────────
            try:
                CachedAdversaryResult.objects.update_or_create(
                    code_hash=code_hash,
                    defaults={
                        "problem_type": problem_type,
                        "response_json": result,
                        "expires_at": timezone.now() + timedelta(hours=12),
                    },
                )
            except Exception as cache_err:
                logger.warning(f"Failed to cache adversary result: {cache_err}")

            self._track_analysis(
                code_hash, user_code, problem_type, "ai_analysis",
                result, total_ms, client_ip
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as ai_err:
            logger.error(f"Adversary LLM Error: {ai_err}")
            return self._heuristic_fallback(
                user_code, problem_type, code_hash, client_ip,
                total_start, str(ai_err)
            )

    def _heuristic_fallback(
        self, user_code, problem_type, code_hash, client_ip, total_start, error_msg
    ):
        """Multi-layer heuristic vulnerability detection fallback."""
        vulnerabilities = []
        feedback_parts = []
        edge_case = "[0, 0, 0]"

        # Memory leak detection
        if "new " in user_code and "delete" not in user_code:
            vulnerabilities.append("memory_leak")
            feedback_parts.append(
                "Memory leak: 'new' allocations without corresponding 'delete' calls."
            )
            edge_case = "Massive insertion set [1...10000] — will exhaust memory."

        # Null pointer dereference
        if "->" in user_code and "nullptr" not in user_code and "NULL" not in user_code:
            vulnerabilities.append("null_dereference")
            feedback_parts.append(
                "Potential null pointer dereference: No null checks before pointer access."
            )
            edge_case = "Empty input / NULL root"

        # Unbalanced tree (sorted input attack)
        if any(kw in user_code.lower() for kw in ["bst", "->left", "->right"]):
            if "rotate" not in user_code.lower() and "balance" not in user_code.lower():
                vulnerabilities.append("unbalanced_tree")
                feedback_parts.append(
                    "Unbalanced BST: No self-balancing mechanism. Sorted input degrades to O(n)."
                )
                edge_case = "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"

        # Duplicate handling
        if "==" not in user_code and any(kw in user_code.lower() for kw in ["insert", "add", "push"]):
            vulnerabilities.append("duplicate_handling")
            feedback_parts.append(
                "No duplicate value handling detected. Duplicate inputs may corrupt the structure."
            )
            edge_case = "[5, 5, 5, 5]"

        # Integer overflow
        if "int " in user_code and "long" not in user_code:
            if any(op in user_code for op in ["*", "sum", "total", "count"]):
                vulnerabilities.append("integer_overflow")
                feedback_parts.append(
                    "Potential integer overflow: Using 'int' for values that may exceed 32-bit range."
                )
                edge_case = "[2147483647, 1]"

        # Array bounds
        if "[" in user_code and "size()" not in user_code and ".length" not in user_code:
            if "for" in user_code:
                vulnerabilities.append("bounds_check")
                feedback_parts.append(
                    "No explicit bounds checking on array access inside loops."
                )

        # Injection detection
        injection = any(
            dangerous in user_code
            for dangerous in ["system(", "exec(", "popen(", "__asm", "fork("]
        )

        if not feedback_parts:
            feedback_parts.append(
                "No obvious vulnerabilities detected via heuristic analysis. "
                "Consider testing with edge cases: empty input, single element, duplicates, and extreme values."
            )

        feedback = " | ".join(feedback_parts)
        severity = "critical" if injection else (
            "high" if len(vulnerabilities) >= 3 else
            "medium" if vulnerabilities else "low"
        )

        total_ms = (time.perf_counter() - total_start) * 1000

        result = {
            "adversary_feedback": f"{feedback} (Heuristic mode: {error_msg[:80]})",
            "edge_case_input": edge_case,
            "injection_attempt_detected": injection,
            "vulnerability_severity": severity,
            "vulnerability_categories": vulnerabilities,
            "rag_context_used": False,
            "source": "heuristic",
            "latency_ms": round(total_ms, 2),
        }


        self._track_analysis(
            code_hash, user_code[:500], "General DSA", "heuristic",
            result, total_ms, client_ip
        )

        return Response(result, status=status.HTTP_200_OK)

    def _track_analysis(
        self, code_hash, user_code, problem_type, source, result, latency_ms, client_ip
    ):
        """Record analysis for analytics."""
        try:
            AdversaryAnalysis.objects.create(
                code_hash=code_hash,
                code_snippet=user_code[:500],
                problem_type=problem_type,
                feedback=result.get("adversary_feedback", "")[:1000],
                edge_case_input=result.get("edge_case_input", ""),
                injection_detected=result.get("injection_attempt_detected", False),
                vulnerability_count=len(result.get("vulnerability_categories", [])),
                source=source,
                latency_ms=latency_ms,
                client_ip=client_ip,
            )
        except Exception as e:
            logger.warning(f"Analytics tracking failed: {e}")

class AdversaryDiagnosticsView(APIView):
    """
    GET /api/v1/adversary/diagnostics/
    """
    def get(self, request):
        total_analyses = AdversaryAnalysis.objects.count()
        injections = AdversaryAnalysis.objects.filter(injection_detected=True).count()
        
        return Response({
            "status": "operational",
            "analytics": {
                "total_analyses": total_analyses,
                "injections_blocked": injections,
                "cached_results": CachedAdversaryResult.objects.count(),
            }
        })
