import os
from typing import Dict, List, Any
from backend.models.simple_schemas import RiskLevel, ClauseAnalysis
import json
import random

class SimpleGPTAnalyzer:
    """Simplified GPT analyzer that provides mock analysis when GPT is not available."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', 'demo_key')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-5')
        self.use_mock = self.api_key == 'demo_key_placeholder' or self.api_key == 'demo_key'
    
    def analyze_clause(self, clause_text: str, legal_context: Dict[str, List[Dict[str, Any]]], clause_id: int) -> ClauseAnalysis:
        """Analyze a clause - mock implementation for demo."""
        
        if self.use_mock:
            return self._mock_analyze_clause(clause_text, legal_context, clause_id)
        
        # Here would be the real GPT implementation
        return self._mock_analyze_clause(clause_text, legal_context, clause_id)
    
    def _mock_analyze_clause(self, clause_text: str, legal_context: Dict[str, List[Dict[str, Any]]], clause_id: int) -> ClauseAnalysis:
        """Mock analysis based on clause content patterns."""
        
        clause_lower = clause_text.lower()
        
        # Simple risk assessment based on keywords
        risk_keywords = {
            'critical': ['nevratný', 'bezpodmínečný', 'neomezený', 'vyloučení', 'zproštění odpovědnosti'],
            'high': ['vyhrazujeme si právo', 'kdykoli změnit', 'bez předchozího upozornění', 'jednostranně'],
            'medium': ['můžeme', 'podle našeho uvážení', 'v případě potřeby'],
            'low': ['informujeme', 'snažíme se', 'doporučujeme']
        }
        
        detected_risk = RiskLevel.LOW
        legal_conflicts = []
        relevant_laws = []
        
        for risk_level, keywords in risk_keywords.items():
            if any(keyword in clause_lower for keyword in keywords):
                if risk_level == 'critical':
                    detected_risk = RiskLevel.CRITICAL
                    legal_conflicts.append("Možné porušení práv spotřebitele")
                    relevant_laws.append("§1815 Občanského zákoníku")
                elif risk_level == 'high' and detected_risk != RiskLevel.CRITICAL:
                    detected_risk = RiskLevel.HIGH
                    legal_conflicts.append("Nerovnováha v právech stran")
                    relevant_laws.append("§1826 Občanského zákoníku")
                elif risk_level == 'medium' and detected_risk not in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                    detected_risk = RiskLevel.MEDIUM
                break
        
        # Generate summary based on risk level
        summaries = {
            RiskLevel.CRITICAL: "Tato klauzule obsahuje velmi problematická ustanovení, která mohou být v rozporu s právem.",
            RiskLevel.HIGH: "Klauzule je jednostranně nevýhodná a může být problematická z právního hlediska.",
            RiskLevel.MEDIUM: "Klauzule vyžaduje pozornost, obsahuje některá sporná ustanovení.",
            RiskLevel.LOW: "Standardní klauzule bez zásadních právních problémů."
        }
        
        explanations = {
            RiskLevel.CRITICAL: "Klauzule obsahuje ustanovení, která mohou být v rozporu s právními předpisy na ochranu spotřebitele a měla by být důkladně přezkoumána právníkem.",
            RiskLevel.HIGH: "Tato klauzule dává službě značnou volnost při změnách podmínek, což může být nevýhodné pro uživatele.",
            RiskLevel.MEDIUM: "Klauzule obsahuje formulace, které mohou být interpretovány různě. Doporučuje se pozornost při akceptaci.",
            RiskLevel.LOW: "Klauzule je formulována standardně a neobsahuje zřejmé právní problémy."
        }
        
        return ClauseAnalysis(
            clause_id=clause_id,
            original_text=clause_text,
            risk_level=detected_risk,
            summary=summaries[detected_risk],
            legal_conflicts=legal_conflicts,
            explanation=explanations[detected_risk],
            relevant_laws=relevant_laws
        )
    
    def generate_overall_summary(self, clause_analyses: List[ClauseAnalysis]) -> str:
        """Generate overall summary."""
        
        risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for analysis in clause_analyses:
            risk_counts[analysis.risk_level.value] += 1
        
        total = len(clause_analyses)
        high_risk = risk_counts['High'] + risk_counts['Critical']
        
        if risk_counts['Critical'] > 0:
            summary = f"KRITICKÉ RIZIKO: Nalezeno {risk_counts['Critical']} kritických klauzulí z celkem {total}. "
            summary += "Doporučujeme konzultaci s právníkem před přijetím těchto podmínek."
        elif risk_counts['High'] > 0:
            summary = f"VYSOKÉ RIZIKO: Nalezeno {risk_counts['High']} vysoce rizikových klauzulí z celkem {total}. "
            summary += "Podmínky obsahují ustanovení, která mohou být problematická."
        elif risk_counts['Medium'] > risk_counts['Low']:
            summary = f"STŘEDNÍ RIZIKO: Většina z {total} klauzulí vyžaduje pozornost. "
            summary += "Doporučuje se pečlivé prostudování před přijetím."
        else:
            summary = f"NÍZKÉ RIZIKO: Z {total} analyzovaných klauzulí většina neobsahuje zásadní problémy. "
            summary += "Podmínky se jeví jako standardní."
        
        return summary