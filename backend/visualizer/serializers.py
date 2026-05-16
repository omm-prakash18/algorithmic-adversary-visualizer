"""
Visualizer Serializers — Input Validation and Response Formatting
"""

from rest_framework import serializers


class CodeToStepsRequestSerializer(serializers.Serializer):
    """Validates incoming code visualization requests."""

    user_code = serializers.CharField(
        required=True,
        min_length=10,
        max_length=50000,
        error_messages={
            "required": "Code is required for visualization.",
            "min_length": "Code must be at least 10 characters.",
            "max_length": "Code exceeds maximum allowed length (50,000 chars).",
        },
    )
    language = serializers.ChoiceField(
        choices=["cpp", "c", "python", "java"],
        default="cpp",
        required=False,
    )
    force_refresh = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Skip cache and force a fresh AI generation",
    )

    def validate_user_code(self, value):
        """Sanitize and validate the submitted code."""
        # Strip null bytes and excessive whitespace
        value = value.replace("\x00", "").strip()
        if not value:
            raise serializers.ValidationError("Code cannot be empty after sanitization.")
        return value


class VisualizationStepSerializer(serializers.Serializer):
    """Serializes individual visualization steps."""

    step = serializers.IntegerField()
    action = serializers.CharField()
    node = serializers.DictField(required=False)
    node_id = serializers.IntegerField(required=False)
    parent_id = serializers.IntegerField(required=False)
    source_id = serializers.IntegerField(required=False)
    target_id = serializers.IntegerField(required=False)
    description = serializers.CharField()
    role = serializers.CharField(required=False)


class CodeToStepsResponseSerializer(serializers.Serializer):
    """Formats the visualization response."""

    steps = VisualizationStepSerializer(many=True)
    source = serializers.CharField()
    detected_algorithm = serializers.CharField(required=False)
    retrieval_time_ms = serializers.FloatField(required=False)
    generation_time_ms = serializers.FloatField(required=False)
    total_time_ms = serializers.FloatField(required=False)
    cached = serializers.BooleanField(default=False)


class DiagnosticsResponseSerializer(serializers.Serializer):
    """Formats the diagnostics endpoint response."""

    status = serializers.CharField()
    version = serializers.CharField()
    rag_engine = serializers.DictField()
    llm_provider = serializers.CharField()
    analytics = serializers.DictField()

    database = serializers.DictField()
    cache = serializers.DictField()
    uptime_seconds = serializers.FloatField()
