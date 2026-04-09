from django.urls import path
from core import views

urlpatterns = [
    path('risk/', views.risk_endpoint, name='risk'),
    path('risk/explain/', views.risk_explain_endpoint, name='risk-explain'),
    path('ml-status/', views.ml_status_endpoint, name='ml-status'),
    path('run-pipeline/', views.run_pipeline_endpoint, name='run-pipeline'),
    path('system-metrics/', views.system_metrics_endpoint, name='system-metrics'),
    path('evaluation-report/', views.evaluation_report_endpoint, name='evaluation-report'),
    path('alerts/', views.alerts_endpoint, name='alerts'),
    path('stats/', views.stats_endpoint, name='stats'),
    path('report/', views.report_endpoint, name='report'),
    path('cities/', views.cities_endpoint, name='cities'),
    path('heatmap/', views.heatmap_endpoint, name='heatmap'),
    path('export/', views.export_csv_view, name='export-csv'),
]
