from django.urls import path
from .views import CodeExecutionView, SandboxDiagnosticsView

urlpatterns = [
    path('execute/', CodeExecutionView.as_view(), name='code-execute'),
    path('diagnostics/', SandboxDiagnosticsView.as_view(), name='sandbox-diagnostics'),
]
