from django.db import models
from django.utils import timezone


class Complaint(models.Model):
    """Raw food adulteration complaint from FSSAI, news, or citizen report."""
    
    SOURCE_CHOICES = [
        ('FSSAI', 'FSSAI'),
        ('NEWS', 'News Article'),
        ('CITIZEN', 'Citizen Report'),
    ]
    
    id = models.AutoField(primary_key=True)
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        help_text="Source of the complaint"
    )
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Tamil Nadu')
    food_item = models.CharField(max_length=100)
    adulterant = models.CharField(max_length=100)
    severity = models.IntegerField(
        help_text="Severity level 1-5"
    )
    raw_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
    
    def __str__(self):
        return f"{self.food_item} - {self.city} - {self.source}"


class RiskScore(models.Model):
    """ML-computed risk score for a food item in a city for a specific month."""
    
    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=100, db_index=True)
    food_item = models.CharField(max_length=100)
    risk_score = models.FloatField(
        help_text="Risk score 0-100"
    )
    adulterant = models.CharField(max_length=100)
    complaint_count = models.IntegerField(default=0)
    month = models.CharField(
        max_length=7,
        help_text="Format: YYYY-MM"
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('city', 'food_item', 'month')
        ordering = ['-risk_score']
        verbose_name = 'Risk Score'
        verbose_name_plural = 'Risk Scores'
    
    def __str__(self):
        return f"{self.food_item} - {self.city} - {self.risk_score}"


class LiveAlert(models.Model):
    """Real-time alert pushed to frontend once created."""
    
    RISK_LEVEL_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    food_item = models.CharField(max_length=100)
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Live Alert'
        verbose_name_plural = 'Live Alerts'
    
    def __str__(self):
        return f"{self.food_item} - {self.city} - {self.risk_level}"
