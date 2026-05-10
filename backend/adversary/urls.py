from django.urls import path
from .views import AdversaryAttackView

urlpatterns = [
    path('attack/', AdversaryAttackView.as_view(), name='adversary-attack'),
]
