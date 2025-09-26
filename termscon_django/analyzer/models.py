from django.db import models
import uuid

# Create your models here.

class RiskLevel(models.TextChoices):
    LOW = "Low", "Low"
    MEDIUM = "Medium", "Medium"
    HIGH = "High", "High"
    CRITICAL = "Critical", "Critical"

class AnalysisSession(models.Model):
    """Store analysis sessions for tracking and potential future reference"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    document_text = models.TextField()
    overall_risk_score = models.CharField(max_length=10, choices=RiskLevel.choices)
    total_clauses = models.IntegerField()
    high_risk_count = models.IntegerField()
    medium_risk_count = models.IntegerField()
    low_risk_count = models.IntegerField()
    overview = models.TextField()

    class Meta:
        ordering = ['-created_at']

class ClauseAnalysisResult(models.Model):
    """Store individual clause analysis results"""
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='clauses')
    clause_id = models.IntegerField()
    original_text = models.TextField()
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    summary = models.TextField()
    legal_conflicts = models.JSONField(default=list)  # List of conflicts
    explanation = models.TextField()
    relevant_laws = models.JSONField(default=list)  # List of relevant laws

    class Meta:
        ordering = ['clause_id']
