from django.urls import path
from . import views

app_name = 'call_analysis'

urlpatterns = [
    path('', views.MainAnalysisView.as_view(), name='main'),
]