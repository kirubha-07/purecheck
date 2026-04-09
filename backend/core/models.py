from django.db import models
from django.utils import timezone
import json


class FoodCategory(models.Model):
    """Classification of food items into categories for risk analysis."""
    
    CATEGORY_CHOICES = [
        ('DAIRY', 'Dairy Products'),
        ('GRAINS', 'Grains & Cereals'),
        ('SPICES', 'Spices & Seasonings'),
        ('OILS', 'Oils & Fats'),
        ('SWEETS', 'Sweets & Confectionery'),
        ('VEGETABLES', 'Vegetables & Fruits'),
        ('PROCESSED', 'Processed Foods'),
        ('OTHERS', 'Others'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    common_adulterants = models.JSONField(default=list, help_text="Common adulterants for this food")
    risk_multiplier = models.FloatField(default=1.0, help_text="Multiplier for base risk score")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['name']),
        ]
        verbose_name = 'Food Category'
        verbose_name_plural = 'Food Categories'
    
    def __str__(self) -> str:
        return f"{self.name} ({self.get_category_display()})"


class Complaint(models.Model):
    """Raw food adulteration complaint from FSSAI, news, or citizen report."""
    
    SOURCE_CHOICES = [
        ('FSSAI', 'FSSAI'),
        ('NEWS', 'News Article'),
        ('CITIZEN', 'Citizen Report'),
    ]
    DATA_SOURCE_TYPE_CHOICES = [
        ('REAL', 'Real'),
        ('SIMULATED', 'Simulated'),
    ]
    NLP_MODE_CHOICES = [
        ('TRANSFORMER', 'Transformer'),
        ('KEYWORD', 'Keyword'),
    ]
    
    id = models.AutoField(primary_key=True)
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        help_text="Source of the complaint"
    )
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, default='Tamil Nadu')
    food_item = models.CharField(max_length=100, db_index=True)
    food_category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )
    adulterant = models.CharField(max_length=100)
    severity = models.IntegerField(
        help_text="Severity level 1-5"
    )
    raw_text = models.TextField()
    nlp_confidence = models.FloatField(
        default=0.0,
        help_text="BERT extraction confidence (0.0-1.0)"
    )
    nlp_mode = models.CharField(
        max_length=20,
        choices=NLP_MODE_CHOICES,
        default='KEYWORD'
    )
    data_source_type = models.CharField(
        max_length=20,
        choices=DATA_SOURCE_TYPE_CHOICES,
        default='SIMULATED'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'food_item']),
            models.Index(fields=['city', 'created_at']),
            models.Index(fields=['source', 'created_at']),
        ]
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
    
    def __str__(self) -> str:
        return f"{self.food_item} - {self.city} - {self.source}"


class RiskScore(models.Model):
    """ML-computed risk score for a food item in a city for a specific month."""
    
    id = models.AutoField(primary_key=True)
    DATA_SOURCE_TYPE_CHOICES = [
        ('REAL', 'Real'),
        ('SIMULATED', 'Simulated'),
    ]
    SCORE_SOURCE_CHOICES = [
        ('ML+RULE', 'ML + Rule Hybrid'),
        ('RULE_ONLY', 'Rule Only'),
    ]

    city = models.CharField(max_length=100, db_index=True)
    food_item = models.CharField(max_length=100)
    food_category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_scores'
    )
    risk_score = models.FloatField(
        help_text="Risk score 0-100"
    )
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Model confidence (0.0-1.0)"
    )
    adulterant = models.CharField(max_length=100)
    complaint_count = models.IntegerField(default=0)
    severity_avg = models.FloatField(default=0.0)
    month = models.CharField(
        max_length=7,
        help_text="Format: YYYY-MM"
    )
    shap_explanation = models.JSONField(
        default=dict,
        blank=True,
        help_text="SHAP feature importance explanation"
    )
    score_source = models.CharField(
        max_length=20,
        choices=SCORE_SOURCE_CHOICES,
        default='RULE_ONLY'
    )
    data_source_type = models.CharField(
        max_length=20,
        choices=DATA_SOURCE_TYPE_CHOICES,
        default='SIMULATED'
    )
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now, help_text="Creation timestamp")
    
    class Meta:
        unique_together = ('city', 'food_item', 'month')
        ordering = ['-risk_score']
        indexes = [
            models.Index(fields=['city', 'month']),
            models.Index(fields=['food_item', 'month']),
            models.Index(fields=['-risk_score']),
        ]
        verbose_name = 'Risk Score'
        verbose_name_plural = 'Risk Scores'
    
    def __str__(self) -> str:
        return f"{self.food_item} - {self.city} - {self.risk_score:.1f}"
    
    def get_shap_explanation(self) -> dict:
        """Parse and return SHAP explanation."""
        return self.shap_explanation if isinstance(self.shap_explanation, dict) else {}


class LiveAlert(models.Model):
    """Real-time alert pushed to frontend once created."""
    
    RISK_LEVEL_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    DATA_SOURCE_TYPE_CHOICES = [
        ('REAL', 'Real'),
        ('SIMULATED', 'Simulated'),
    ]
    
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    food_item = models.CharField(max_length=100)
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES
    )
    risk_score = models.FloatField(default=0.0)
    evidence = models.JSONField(
        default=list,
        help_text="List of evidence items supporting the alert"
    )
    data_source_type = models.CharField(
        max_length=20,
        choices=DATA_SOURCE_TYPE_CHOICES,
        default='SIMULATED'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'created_at']),
            models.Index(fields=['risk_level', 'created_at']),
        ]
        verbose_name = 'Live Alert'
        verbose_name_plural = 'Live Alerts'
    
    def __str__(self) -> str:
        return f"{self.food_item} - {self.city} - {self.risk_level}"


class UserReport(models.Model):
    """Citizen-submitted food adulteration reports with optional image upload."""
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('PROCESSING', 'Processing'),
        ('VERIFIED', 'Verified'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=100, db_index=True)
    food_item = models.CharField(max_length=100)
    food_category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_reports'
    )
    adulterant = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to='reports/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Photo of the suspected adulterated product"
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED'
    )
    severity_estimate = models.IntegerField(
        default=2,
        help_text="1-5 scale, estimated by user"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        verbose_name = 'User Report'
        verbose_name_plural = 'User Reports'
    
    def __str__(self) -> str:
        return f"Report: {self.food_item} in {self.city} ({self.status})"


class AuditLog(models.Model):
    """Track all automated pipeline runs with status and performance metrics."""
    
    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('SCRAPING', 'Scraping Data'),
        ('EXTRACTING', 'Extracting Entities'),
        ('SCORING', 'Calculating Scores'),
        ('ALERTING', 'Generating Alerts'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.AutoField(primary_key=True)
    pipeline_run_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique ID for this pipeline execution"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    current_step = models.CharField(max_length=100, blank=True)
    
    # Metrics
    complaints_scraped = models.IntegerField(default=0)
    complaints_new = models.IntegerField(default=0)
    complaints_processed = models.IntegerField(default=0)
    risk_scores_updated = models.IntegerField(default=0)
    alerts_generated = models.IntegerField(default=0)
    
    # Performance
    duration_seconds = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['-started_at']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self) -> str:
        duration = self.duration_seconds or 0
        return f"Pipeline {self.pipeline_run_id} - {self.status} ({duration:.2f}s)"
    
    def mark_completed(self) -> None:
        """Mark pipeline as completed and calculate duration."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()
    
    def mark_failed(self, error: str) -> None:
        """Mark pipeline as failed with error message."""
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        self.error_message = error[:500]  # Truncate to 500 chars
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.save()


class PipelineConfig(models.Model):
    """Configuration for automated pipeline runs."""
    
    FREQUENCY_CHOICES = [
        ('6h', 'Every 6 hours'),
        ('12h', 'Every 12 hours'),
        ('24h', 'Every 24 hours'),
    ]
    
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=5,
        choices=FREQUENCY_CHOICES,
        default='6h'
    )
    next_run_at = models.DateTimeField(default=timezone.now)
    
    # Scraper settings
    enable_news_scraping = models.BooleanField(default=True)
    enable_fssai_scraping = models.BooleanField(default=True)
    enable_forum_scraping = models.BooleanField(default=False)
    
    # Processing settings
    bert_confidence_threshold = models.FloatField(default=0.6)
    minimum_complaints_for_alert = models.IntegerField(default=3)
    alert_risk_threshold = models.FloatField(default=70.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pipeline Configuration'
        verbose_name_plural = 'Pipeline Configurations'
    
    def __str__(self) -> str:
        return f"Pipeline Config - {self.get_frequency_display()} - {'Active' if self.is_active else 'Inactive'}"
