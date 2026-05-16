"""
Adversary Serializers — Input Validation and Response Formatting
"""

from rest_framework import serializers


class AdversaryAttackRequestSerializer(serializers.Serializer):
    """Validates incoming adversary attack requests."""

    user_code = serializers.CharField(
        required=True,
        min_length=10,
        max_length=50000,
        error_messages={
            "required": "Code is required for adversarial analysis.",
            "min_length": "Code must be at least 10 characters.",
        },
    )
    problem_type = serializers.CharField(
        default="General DSA",
        max_length=128,
        required=False,
    )
    force_refresh = serializers.BooleanField(default=False, required=False)

    def validate_user_code(self, value):
        value = value.replace("\x00", "").strip()
        if not value:
            raise serializers.ValidationError("Code cannot be empty after sanitization.")
        return value


class AdversaryAttackResponseSerializer(serializers.Serializer):
    """Formats the adversary attack response."""

    adversary_feedback = serializers.CharField()
    edge_case_input = serializers.CharField()
    injection_attempt_detected = serializers.BooleanField()
    vulnerability_severity = serializers.CharField(required=False)
    vulnerability_categories = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    rag_context_used = serializers.BooleanField(required=False, default=False)
    source = serializers.CharField(required=False)
    latency_ms = serializers.FloatField(required=False)

