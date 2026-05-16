"""
Sandbox Serializers — Input Validation and Security
"""

import re
from rest_framework import serializers


# Dangerous patterns that should be blocked in sandboxed execution
DANGEROUS_PATTERNS = [
    (r'#\s*include\s*<\s*fstream\s*>', "File I/O (fstream) is not allowed in sandbox"),
    (r'system\s*\(', "system() calls are blocked for security"),
    (r'exec[lv]?p?\s*\(', "exec() family calls are blocked"),
    (r'fork\s*\(', "fork() is blocked in sandbox"),
    (r'popen\s*\(', "popen() is blocked for security"),
    (r'__asm', "Inline assembly is not allowed"),
    (r'#\s*include\s*<\s*windows\.h\s*>', "Windows API access is blocked"),
    (r'#\s*include\s*<\s*unistd\.h\s*>', "POSIX API access is restricted"),
    (r'#\s*include\s*<\s*sys/', "System headers are restricted"),
    (r'socket\s*\(', "Network operations are blocked"),
    (r'remove\s*\(\s*"', "File deletion is blocked"),
    (r'rename\s*\(\s*"', "File operations are blocked"),
]


class CodeExecutionRequestSerializer(serializers.Serializer):
    """Validates and sanitizes code execution requests."""

    user_code = serializers.CharField(
        required=True,
        min_length=10,
        max_length=50000,
    )
    stdin_input = serializers.CharField(
        default="",
        required=False,
        max_length=10000,
        help_text="Optional stdin input for the program",
    )
    timeout_seconds = serializers.IntegerField(
        default=2,
        min_value=1,
        max_value=5,
        required=False,
    )

    def validate_user_code(self, value):
        value = value.replace("\x00", "").strip()
        if not value:
            raise serializers.ValidationError("Code cannot be empty.")

        # Security scan
        security_flags = []
        for pattern, message in DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                security_flags.append(message)

        if security_flags:
            raise serializers.ValidationError(
                f"Security violation(s) detected: {'; '.join(security_flags)}"
            )

        return value


class CodeExecutionResponseSerializer(serializers.Serializer):
    """Formats the execution response."""

    status = serializers.CharField()
    stdout = serializers.CharField(required=False, allow_blank=True)
    stderr = serializers.CharField(required=False, allow_blank=True)
    execution_time_ms = serializers.FloatField(required=False)
    memory_used_kb = serializers.IntegerField(required=False)
    error = serializers.CharField(required=False)
