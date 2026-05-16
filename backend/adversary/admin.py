from django.contrib import admin
from .models import AdversaryAnalysis, CachedAdversaryResult


@admin.register(AdversaryAnalysis)
class AdversaryAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem_type', 'source', 'vulnerability_count', 'injection_detected', 'latency_ms', 'created_at']
    list_filter = ['source', 'injection_detected', 'problem_type', 'created_at']
    search_fields = ['code_hash', 'code_snippet', 'feedback']
    readonly_fields = ['code_hash', 'created_at']
    ordering = ['-created_at']


@admin.register(CachedAdversaryResult)
class CachedAdversaryResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'code_hash', 'problem_type', 'hit_count', 'created_at', 'expires_at']
    list_filter = ['problem_type', 'created_at']
    readonly_fields = ['code_hash', 'created_at']
