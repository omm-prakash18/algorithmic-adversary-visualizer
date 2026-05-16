"""
Sandbox Models — Execution History and Security Tracking
"""

import hashlib
from django.db import models


class ExecutionRecord(models.Model):
    """Records every code execution for analytics, auditing, and security."""

    code_hash = models.CharField(max_length=64, db_index=True)
    code_snippet = models.TextField(help_text="First 500 chars of submitted code")
    language = models.CharField(max_length=16, default="cpp")
    status = models.CharField(
        max_length=32,
        choices=[
            ("success", "Success"),
            ("compilation_error", "Compilation Error"),
            ("runtime_error", "Runtime Error"),
            ("timeout", "Timeout"),
            ("security_blocked", "Security Blocked"),
            ("mock_success", "Mock Success"),
        ],
        default="success",
        db_index=True,
    )
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    execution_time_ms = models.FloatField(default=0.0)
    memory_used_kb = models.IntegerField(default=0)
    security_flags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of security violations detected",
    )
    client_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Exec#{self.pk} [{self.status}] {self.execution_time_ms:.0f}ms"

    @staticmethod
    def compute_code_hash(code: str) -> str:
        return hashlib.sha256(code.strip().encode()).hexdigest()
