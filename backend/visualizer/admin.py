from django.contrib import admin
from .models import VisualizationRequest, CachedVisualization


@admin.register(VisualizationRequest)
class VisualizationRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'detected_algorithm', 'source', 'step_count', 'latency_ms', 'created_at']
    list_filter = ['source', 'detected_algorithm', 'created_at']
    search_fields = ['code_hash', 'code_snippet']
    readonly_fields = ['code_hash', 'created_at']
    ordering = ['-created_at']


@admin.register(CachedVisualization)
class CachedVisualizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'code_hash', 'hit_count', 'created_at', 'expires_at']
    list_filter = ['created_at']
    readonly_fields = ['code_hash', 'created_at']
