"""
Adversary Models — Attack History and Vulnerability Tracking
"""

import hashlib
from django.db import models


class AdversaryAnalysis(models.Model):
    """Records every adversarial analysis for pattern tracking."""

    code_hash = models.CharField(max_length=64, db_index=True)
    code_snippet = models.TextField(help_text="First 500 chars of submitted code")
    problem_type = models.CharField(max_length=128, default="General DSA")
    feedback = models.TextField(blank=True)
    edge_case_input = models.TextField(blank=True)
    injection_detected = models.BooleanField(default=False)
    vulnerability_count = models.IntegerField(default=0)
    source = models.CharField(
        max_length=32,
        choices=[
            ("ai_analysis", "AI Analysis"),
            ("heuristic", "Heuristic Fallback"),
            ("cached", "Cache Hit"),
        ],
        default="ai_analysis",
    )
    latency_ms = models.FloatField(default=0.0)
    client_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Adversary Analyses"

    def __str__(self):
        return f"Attack#{self.pk} [{self.problem_type}] vulns={self.vulnerability_count}"

    @staticmethod
    def compute_code_hash(code: str) -> str:
        return hashlib.sha256(code.strip().encode()).hexdigest()


class CachedAdversaryResult(models.Model):
    """Persistent cache for adversary analysis results."""

    code_hash = models.CharField(max_length=64, db_index=True)
    problem_type = models.CharField(max_length=128)
    response_json = models.JSONField()
    hit_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("code_hash", "problem_type")


    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @classmethod
    def get_or_none(cls, code_hash: str, problem_type: str):
        try:
            entry = cls.objects.get(code_hash=code_hash, problem_type=problem_type)
            if entry.is_expired:
                entry.delete()
                return None
            entry.hit_count += 1
            entry.save(update_fields=["hit_count"])
            return entry
        except cls.DoesNotExist:
            return None
