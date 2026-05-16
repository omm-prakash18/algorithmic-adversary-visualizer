"""
Visualizer Views (v2.0) — High-Performance RAG Pipeline
=========================================================
- ChromaDB-backed RAG with MMR retrieval and query caching
- Persistent response caching via Django models
- Full analytics tracking with latency breakdown
- Async-ready architecture with proper serializer validation
- Graceful degradation with intelligent fallback
"""

import logging
import os
import re
import time
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CachedVisualization, VisualizationRequest, KnowledgeDocument
from .rag_engine import get_rag_engine
from .serializers import CodeToStepsRequestSerializer, DiagnosticsResponseSerializer

from .llm_factory import get_llm_chain

logger = logging.getLogger(__name__)

# Cache chains per process
_chains = {}

def _get_cached_chain(api_key: str, app_type: str):
    key = f"{api_key[:10]}_{app_type}"
    if key not in _chains:
        _chains[key] = get_llm_chain(api_key, app_type)
    return _chains[key]



def get_client_ip(request) -> str:
    """Extract client IP from request, handling proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


class CodeToStepsView(APIView):
    """
    POST /api/v1/visualize/generate-steps/

    Converts user code into visualization steps using a RAG-augmented LLM pipeline.
    Features:
    - Input validation via serializers
    - Persistent response caching (DB-backed)
    - RAG context from ChromaDB with MMR retrieval
    - Full analytics tracking
    - Graceful fallback to local BST simulation
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
        serializer = CodeToStepsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_code = serializer.validated_data["user_code"]
        force_refresh = serializer.validated_data.get("force_refresh", False)
        code_hash = VisualizationRequest.compute_code_hash(user_code)
        client_ip = get_client_ip(request)

        # ── 2. Check Persistent Cache ────────────────────────
        if not force_refresh:
            cached = CachedVisualization.get_or_none(code_hash)
            if cached:
                total_ms = (time.perf_counter() - total_start) * 1000

                # Track the cache hit
                VisualizationRequest.objects.create(
                    code_hash=code_hash,
                    code_snippet=user_code[:500],
                    source="cached",
                    step_count=len(cached.response_json.get("steps", [])),
                    latency_ms=total_ms,
                    client_ip=client_ip,
                )

                response_data = cached.response_json.copy()
                response_data["cached"] = True
                response_data["total_time_ms"] = round(total_ms, 2)
                return Response(response_data, status=status.HTTP_200_OK)

        # ── 3. Check for Active API Key ──────────────────────
        api_key = self._get_active_api_key()
        if not api_key:
            logger.warning("No active API key found (OpenAI/Google), falling back to local simulation")
            return self._fallback_local_simulation(
                user_code, code_hash, client_ip, total_start, "No valid API key in .env"
            )

        # ── 4. RAG Retrieval ─────────────────────────────────
        rag_start = time.perf_counter()
        try:
            rag_engine = get_rag_engine()
            context = rag_engine.get_context_string(user_code, k=4, use_mmr=True)
            detected_algo = rag_engine.detect_algorithm_category(user_code)
        except Exception as rag_err:
            logger.warning(f"RAG retrieval failed, proceeding without context: {rag_err}")
            context = ""
            detected_algo = None
        rag_ms = (time.perf_counter() - rag_start) * 1000

        # ── 4. LLM Generation ───────────────────────────────
        llm_start = time.perf_counter()
        try:
            chain = _get_cached_chain(api_key, "visualizer")
            result = chain.invoke({"context": context, "code": user_code})

            steps = result.get("steps", result) if isinstance(result, dict) else result
            llm_ms = (time.perf_counter() - llm_start) * 1000
            total_ms = (time.perf_counter() - total_start) * 1000

            response_data = {
                "steps": steps,
                "source": "rag_professional",
                "detected_algorithm": detected_algo,
                "retrieval_time_ms": round(rag_ms, 2),
                "generation_time_ms": round(llm_ms, 2),
                "total_time_ms": round(total_ms, 2),
                "cached": False,
            }

            # ── 5. Cache the Response ────────────────────────
            try:
                CachedVisualization.objects.update_or_create(
                    code_hash=code_hash,
                    defaults={
                        "response_json": response_data,
                        "expires_at": timezone.now() + timedelta(hours=24),
                    },
                )
            except Exception as cache_err:
                logger.warning(f"Failed to cache visualization: {cache_err}")

            # ── 6. Track Analytics ───────────────────────────
            try:
                VisualizationRequest.objects.create(
                    code_hash=code_hash,
                    code_snippet=user_code[:500],
                    detected_algorithm=detected_algo,
                    source="rag_professional",
                    step_count=len(steps) if isinstance(steps, list) else 0,
                    latency_ms=total_ms,
                    rag_retrieval_ms=rag_ms,
                    llm_generation_ms=llm_ms,
                    client_ip=client_ip,
                )
            except Exception as track_err:
                logger.warning(f"Analytics tracking failed: {track_err}")

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as ai_err:
            logger.error(f"LLM Pipeline Error: {ai_err}")
            return self._fallback_local_simulation(
                user_code, code_hash, client_ip, total_start, str(ai_err)
            )

    def _fallback_local_simulation(
        self, user_code: str, code_hash: str, client_ip: str, total_start: float, error_msg: str
    ):
        """
        Intelligent local fallback that extracts numbers from code
        and simulates a BST insertion for visualization.
        """
        nums = [int(n) for n in re.findall(r"\d+", user_code)]
        test_data = nums[:10] if nums else [10, 5, 15, 3, 7]

        steps = []
        node_counter = 0

        class SimpleBSTNode:
            def __init__(self, val, node_id):
                self.val, self.id = val, node_id
                self.left = self.right = None

        root = None
        for val in test_data:
            if root is None:
                root = SimpleBSTNode(val, node_counter)
                steps.append({
                    "step": len(steps) + 1,
                    "action": "create_root",
                    "node": {"id": node_counter, "value": val, "role": "Root Node"},
                    "description": f"AI offline: Tree is empty. Creating the root node with value {val}.",
                })
                node_counter += 1
            else:
                curr = root
                while True:
                    steps.append({
                        "step": len(steps) + 1,
                        "action": "compare",
                        "node_id": curr.id,
                        "role": "Current Node",
                        "description": f"AI offline: Comparing value ({val}) against node ({curr.val}).",
                    })
                    if val < curr.val:
                        if curr.left is None:
                            curr.left = SimpleBSTNode(val, node_counter)
                            steps.append({
                                "step": len(steps) + 1,
                                "action": "insert_left",
                                "parent_id": curr.id,
                                "node": {"id": node_counter, "value": val, "role": "New Left Child"},
                                "description": f"AI offline: {val} < {curr.val}, inserting as left child.",
                            })
                            node_counter += 1
                            break
                        curr = curr.left
                    else:
                        if curr.right is None:
                            curr.right = SimpleBSTNode(val, node_counter)
                            steps.append({
                                "step": len(steps) + 1,
                                "action": "insert_right",
                                "parent_id": curr.id,
                                "node": {"id": node_counter, "value": val, "role": "New Right Child"},
                                "description": f"AI offline: {val} >= {curr.val}, inserting as right child.",
                            })
                            node_counter += 1
                            break
                        curr = curr.right

        total_ms = (time.perf_counter() - total_start) * 1000

        # Track fallback analytics
        try:
            VisualizationRequest.objects.create(
                code_hash=code_hash,
                code_snippet="[fallback]",
                source="fallback_local",
                step_count=len(steps),
                latency_ms=total_ms,
                client_ip=client_ip,
            )
        except Exception:
            pass

        return Response(
            {
                "steps": steps,
                "source": "fallback_local",
                "warning": f"AI currently unavailable ({error_msg[:100]}). Using local simulation.",
                "total_time_ms": round(total_ms, 2),
            },
            status=status.HTTP_200_OK,
        )


import psutil

# Track start time for uptime
START_TIME = time.time()

# Global Version Configuration
VERSION = "v2.2-EXPERT-HARDENED"

class VisualizerDiagnosticsView(APIView):
    """
    GET /api/v1/visualize/diagnostics/
    """

    def get(self, request):
        try:
            rag_engine = get_rag_engine()
            rag_stats = rag_engine.get_stats()
        except Exception:
            rag_stats = {"initialized": False, "error": "Failed to load RAG engine"}

        # Analytics summary
        total_requests = VisualizationRequest.objects.count()
        cache_hits = VisualizationRequest.objects.filter(source="cached").count()
        avg_latency = 0
        if total_requests > 0:
            from django.db.models import Avg
            avg_latency = VisualizationRequest.objects.aggregate(
                avg=Avg("latency_ms")
            )["avg"] or 0

        # Detect LLM Provider
        api_key = os.getenv("OPENAI_API_KEY", "")
        provider = "None"
        if api_key.startswith("sk-") and "exhausted" not in api_key.lower():
            provider = "OpenAI (gpt-4o-mini)"
        else:
            google_key = os.getenv("GOOGLE_API_KEY", "")
            if google_key:
                provider = "Google Gemini (gemini-1.5-flash)"

        data = {
            "status": "operational",
            "version": VERSION,
            "rag_engine": rag_stats,
            "llm_provider": provider,
            "analytics": {
                "total_requests": total_requests,
                "cache_hits": cache_hits,
                "cache_hit_rate": f"{(cache_hits / max(total_requests, 1)) * 100:.1f}%",
                "avg_latency_ms": round(avg_latency, 2),
            },
            "database": {
                "cached_visualizations": CachedVisualization.objects.count(),
                "knowledge_documents": KnowledgeDocument.objects.count(),
            },
            "cache": {
                "size": rag_stats.get("cache_size", 0),
                "ttl": rag_stats.get("cache_ttl_seconds", 0),
            },
            "uptime_seconds": round(time.time() - START_TIME, 2),
        }
        
        # Validate with serializer
        serializer = DiagnosticsResponseSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


