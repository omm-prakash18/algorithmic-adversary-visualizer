"""
URL configuration for config project (v2.0)
=============================================
Includes all API endpoints, diagnostics, and health checks.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


from visualizer.views import VERSION

@api_view(['GET'])
def api_root(request, format=None):
    """API root endpoint with full endpoint discovery."""
    return Response({
        "status": "online",
        "version": VERSION,
        "engine": "Algorithmic Intelligence Core",
        "endpoints": {
            "sandbox": {
                "execute": reverse('code-execute', request=request, format=format),
                "diagnostics": reverse('sandbox-diagnostics', request=request, format=format),
            },
            "adversary": {
                "attack": reverse('adversary-attack', request=request, format=format),
                "diagnostics": reverse('adversary-diagnostics', request=request, format=format),
            },
            "visualizer": {
                "generate_steps": reverse('generate-steps', request=request, format=format),
                "diagnostics": reverse('visualizer-diagnostics', request=request, format=format),
            },
        },
        "features": [
            "Expert-Hardened LLM Factory (OpenAI/Gemini)",
            "Dynamic Database-Backed RAG Knowledge Base",
            "Multi-Collection Vector Retrieval",
            "Security-Hardened C++ Sandbox Execution",
            "Real-time System Observability and Analytics",
        ],
    })


@api_view(['GET'])
def health_check(request, format=None):
    """Lightweight health check for monitoring."""
    import time
    from django.db import connection
    
    db_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        pass
    
    return Response({
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": time.time(),
    })


urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/v1/', api_root),
    path('api/v1/health/', health_check, name='health-check'),
    path('api/v1/sandbox/', include('sandbox.urls')),
    path('api/v1/adversary/', include('adversary.urls')),
    path('api/v1/visualize/', include('visualizer.urls')),
]
