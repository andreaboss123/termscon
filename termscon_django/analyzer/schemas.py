from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ClauseAnalysis(BaseModel):
    clause_id: int
    original_text: str
    risk_level: RiskLevel
    summary: str
    legal_conflicts: List[str]
    explanation: str
    relevant_laws: List[str]

class OverallSummary(BaseModel):
    overall_risk_score: RiskLevel
    total_clauses: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    overview: str

class AnalysisResult(BaseModel):
    document_id: str
    overall_summary: OverallSummary
    clause_analyses: List[ClauseAnalysis]

class DocumentUpload(BaseModel):
    content: str
    filename: Optional[str] = None