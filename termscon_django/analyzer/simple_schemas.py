from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

@dataclass
class ClauseAnalysis:
    clause_id: int
    original_text: str
    risk_level: RiskLevel
    summary: str
    legal_conflicts: List[str]
    explanation: str
    relevant_laws: List[str]

@dataclass
class OverallSummary:
    overall_risk_score: RiskLevel
    total_clauses: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    overview: str

@dataclass
class AnalysisResult:
    document_id: str
    overall_summary: OverallSummary
    clause_analyses: List[ClauseAnalysis]

@dataclass
class DocumentUpload:
    content: str
    filename: Optional[str] = None