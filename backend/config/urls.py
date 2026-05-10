"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        "status": "online",
        "version": "v4.0-CORE",
        "endpoints": {
            "sandbox": reverse('code-execute', request=request, format=format),
            "adversary": reverse('adversary-attack', request=request, format=format),
            "visualize": reverse('generate-steps', request=request, format=format)
        },
        "message": "Algorithmic Adversary Neural Uplink Active."
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api_root),
    path('api/v1/sandbox/', include('sandbox.urls')),
    path('api/v1/adversary/', include('adversary.urls')),
    path('api/v1/visualize/', include('visualizer.urls')),
]
