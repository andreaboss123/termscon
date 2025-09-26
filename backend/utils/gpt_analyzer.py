import os
from openai import OpenAI
from typing import Dict, List, Any
from backend.models.schemas import RiskLevel, ClauseAnalysis
import json

class GPTAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', 'demo_key'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    def analyze_clause(self, clause_text: str, legal_context: Dict[str, List[Dict[str, Any]]], clause_id: int) -> ClauseAnalysis:
        """Analyze a single T&C clause against legal context using GPT-5."""
        
        # Prepare the legal context for the prompt
        civil_context = "\n".join([
            f"- {item['text'][:200]}..." if len(item['text']) > 200 else f"- {item['text']}"
            for item in legal_context.get('civil_code', [])[:3]
        ])
        
        criminal_context = "\n".join([
            f"- §{item.get('paragraph_number', 'N/A')}: {item['text'][:200]}..." if len(item['text']) > 200 else f"- §{item.get('paragraph_number', 'N/A')}: {item['text']}"
            for item in legal_context.get('criminal_code', [])[:3]
        ])
        
        prompt = f"""
        Analyzuj následující klauzuli z obchodních podmínek vzhledem k českému právu.

        KLAUZULE K ANALÝZE:
        {clause_text}

        RELEVANTNÍ USTANOVENÍ OBČANSKÉHO ZÁKONÍKU:
        {civil_context}

        RELEVANTNÍ USTANOVENÍ TRESTNÍHO ZÁKONÍKU:
        {criminal_context}

        Proveď analýzu a poskytni odpověď ve formátu JSON s následujícími položkami:
        {{
            "risk_level": "Low/Medium/High/Critical",
            "summary": "Jednoduché shrnutí co klauzule znamená pro uživatele (max 150 slov)",
            "legal_conflicts": ["seznam možných konfliktů s právem"],
            "explanation": "Podrobné vysvětlení proč je klauzule problematická, včetně konkrétních odkazů na paragrafy (pokud jsou konflikty)",
            "relevant_laws": ["§1815 Občanského zákoníku", "§XYZ Trestního zákoníku"]
        }}

        Hodnotící kritéria pro riziko:
        - Low: Standardní klauzule bez právních problémů
        - Medium: Potenciálně problematická, ale obvykle vymahatelná
        - High: Pravděpodobně neplatná nebo nespravedlivá vůči spotřebiteli
        - Critical: Jasně v rozporu s právem nebo extrémně nespravedlivá

        Odpovídej pouze v JSON formátu bez dalšího textu.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Jsi právní expert specializující se na české právo a analýzu obchodních podmínek. Odpovídáš pouze v JSON formátu."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                analysis_data = {
                    "risk_level": "Medium",
                    "summary": "Analýza nebyla dokončena kvůli technické chybě.",
                    "legal_conflicts": [],
                    "explanation": "Nepodařilo se dokončit analýzu této klauzule.",
                    "relevant_laws": []
                }
            
            return ClauseAnalysis(
                clause_id=clause_id,
                original_text=clause_text,
                risk_level=RiskLevel(analysis_data.get("risk_level", "Medium")),
                summary=analysis_data.get("summary", ""),
                legal_conflicts=analysis_data.get("legal_conflicts", []),
                explanation=analysis_data.get("explanation", ""),
                relevant_laws=analysis_data.get("relevant_laws", [])
            )
            
        except Exception as e:
            print(f"Error in GPT analysis: {e}")
            # Return a fallback analysis
            return ClauseAnalysis(
                clause_id=clause_id,
                original_text=clause_text,
                risk_level=RiskLevel.MEDIUM,
                summary="Analýza nebyla dokončena kvůli technické chybě.",
                legal_conflicts=[],
                explanation=f"Chyba při analýze: {str(e)}",
                relevant_laws=[]
            )
    
    def generate_overall_summary(self, clause_analyses: List[ClauseAnalysis]) -> str:
        """Generate an overall summary of the T&C analysis."""
        
        risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for analysis in clause_analyses:
            risk_counts[analysis.risk_level.value] += 1
        
        high_risk_clauses = [a for a in clause_analyses if a.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        
        prompt = f"""
        Na základě analýzy {len(clause_analyses)} klauzulí obchodních podmínek poskytni celkové shrnutí:

        STATISTIKY RIZIK:
        - Nízké riziko: {risk_counts['Low']} klauzulí
        - Střední riziko: {risk_counts['Medium']} klauzulí  
        - Vysoké riziko: {risk_counts['High']} klauzulí
        - Kritické riziko: {risk_counts['Critical']} klauzulí

        VYSOCE RIZIKOVÉ KLAUZULE:
        {chr(10).join([f"- {a.summary[:100]}..." for a in high_risk_clauses[:3]])}

        Vytvoř stručné shrnutí (max 200 slov) které:
        1. Zhodnotí celkovou rizikovost podmínek
        2. Upozorní na hlavní problematické oblasti
        3. Doporučí dalši kroky pro uživatele
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Jsi právní expert. Poskytni stručné a srozumitelné shrnutí pro běžného uživatele."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Celkové shrnutí: Analyzováno {len(clause_analyses)} klauzulí s {risk_counts['High'] + risk_counts['Critical']} vysoce rizikovými ustanoveními."