from django.urls import path
from .views import AdversaryAttackView, AdversaryDiagnosticsView

urlpatterns = [
    path('attack/', AdversaryAttackView.as_view(), name='adversary-attack'),
    path('diagnostics/', AdversaryDiagnosticsView.as_view(), name='adversary-diagnostics'),
]
