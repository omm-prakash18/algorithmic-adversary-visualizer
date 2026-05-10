from django.urls import path
from .views import CodeToStepsView

urlpatterns = [
    path('generate-steps/', CodeToStepsView.as_view(), name='generate-steps'),
]
