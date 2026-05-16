from django.contrib import admin
from .models import ExecutionRecord


@admin.register(ExecutionRecord)
class ExecutionRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'language', 'execution_time_ms', 'memory_used_kb', 'created_at']
    list_filter = ['status', 'language', 'created_at']
    search_fields = ['code_hash', 'code_snippet', 'stdout', 'stderr']
    readonly_fields = ['code_hash', 'created_at']
    ordering = ['-created_at']
