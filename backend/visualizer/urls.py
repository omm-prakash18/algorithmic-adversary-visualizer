from django.urls import path
from .views import CodeToStepsView, VisualizerDiagnosticsView

urlpatterns = [
    path('generate-steps/', CodeToStepsView.as_view(), name='generate-steps'),
    path('diagnostics/', VisualizerDiagnosticsView.as_view(), name='visualizer-diagnostics'),
]
