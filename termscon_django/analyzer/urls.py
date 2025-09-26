from django.urls import path
from . import views

app_name = 'termscon_django.analyzer'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/analyze/', views.analyze_document, name='analyze'),
    path('api/health/', views.health_check, name='health'),
    path('history/', views.analysis_history, name='history'),
    path('analysis/<uuid:session_id>/', views.analysis_detail, name='detail'),
]