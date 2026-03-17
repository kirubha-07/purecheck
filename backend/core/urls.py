from django.urls import path
from core import views

urlpatterns = [
    path('risk/', views.risk_endpoint, name='risk'),
    path('alerts/', views.alerts_endpoint, name='alerts'),
    path('report/', views.report_endpoint, name='report'),
    path('cities/', views.cities_endpoint, name='cities'),
]
