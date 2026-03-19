from django.urls import path
from core import views

urlpatterns = [
    path('risk/', views.risk_endpoint, name='risk'),
    path('risk/explain/', views.risk_explain_endpoint, name='risk-explain'),
    path('alerts/', views.alerts_endpoint, name='alerts'),
    path('report/', views.report_endpoint, name='report'),
    path('cities/', views.cities_endpoint, name='cities'),
    path('heatmap/', views.heatmap_endpoint, name='heatmap'),
]
