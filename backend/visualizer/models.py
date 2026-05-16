"""
Visualizer Models — Analytics, Caching, and Knowledge Management
"""

import hashlib
from django.db import models
from django.utils import timezone


class VisualizationRequest(models.Model):
    """Tracks every visualization request for analytics and rate limiting."""

    code_hash = models.CharField(max_length=64, db_index=True, help_text="SHA-256 hash of submitted code")
    code_snippet = models.TextField(help_text="First 500 chars of submitted code for debugging")
    detected_algorithm = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    source = models.CharField(
        max_length=32,
        choices=[
            ("rag_professional", "RAG + LLM"),
            ("fallback_local", "Local Simulation"),
            ("cached", "Cache Hit"),
        ],
        default="rag_professional",
    )
    step_count = models.IntegerField(default=0)
    latency_ms = models.FloatField(default=0.0, help_text="End-to-end processing time in ms")
    rag_retrieval_ms = models.FloatField(default=0.0, help_text="RAG retrieval time in ms")
    llm_generation_ms = models.FloatField(default=0.0, help_text="LLM generation time in ms")
    client_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code_hash", "created_at"]),
            models.Index(fields=["detected_algorithm", "created_at"]),
        ]

    def __str__(self):
        return f"Viz#{self.pk} [{self.detected_algorithm or 'unknown'}] {self.source} ({self.latency_ms:.0f}ms)"

    @staticmethod
    def compute_code_hash(code: str) -> str:
        return hashlib.sha256(code.strip().encode()).hexdigest()


class CachedVisualization(models.Model):
    """
    Persistent cache for LLM-generated visualization responses.
    Avoids redundant API calls for identical code submissions.
    """

    code_hash = models.CharField(max_length=64, unique=True, db_index=True)
    response_json = models.JSONField(help_text="The cached steps JSON response")
    hit_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Cache expiration time")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cache#{self.pk} hits={self.hit_count}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @classmethod
    def get_or_none(cls, code_hash: str):
        try:
            entry = cls.objects.get(code_hash=code_hash)
            if entry.is_expired:
                entry.delete()
                return None
            entry.hit_count += 1
            entry.save(update_fields=["hit_count"])
            return entry
        except cls.DoesNotExist:
            return None

class KnowledgeDocument(models.Model):
    """Stores documents for the RAG engine knowledge base."""

    collection_name = models.CharField(max_length=64, db_index=True)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.collection_name}] {self.content[:50]}..."
