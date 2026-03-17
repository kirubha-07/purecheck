from django.contrib import admin
from core.models import Complaint, RiskScore, LiveAlert


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'city', 'food_item', 'adulterant', 'severity', 'created_at')
    list_filter = ('source', 'city', 'created_at', 'severity')
    search_fields = ('city', 'food_item', 'adulterant')
    readonly_fields = ('created_at', 'raw_text')
    date_hierarchy = 'created_at'


@admin.register(RiskScore)
class RiskScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'food_item', 'risk_score', 'month', 'complaint_count', 'last_updated')
    list_filter = ('city', 'month', 'last_updated')
    search_fields = ('city', 'food_item')
    readonly_fields = ('last_updated',)
    date_hierarchy = 'last_updated'


@admin.register(LiveAlert)
class LiveAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'food_item', 'risk_level', 'created_at')
    list_filter = ('city', 'risk_level', 'created_at')
    search_fields = ('city', 'food_item')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
