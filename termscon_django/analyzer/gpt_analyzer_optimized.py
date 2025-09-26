import os
from openai import OpenAI
from typing import Dict, List, Any
from .simple_schemas import RiskLevel, ClauseAnalysis
import json

class OptimizedGPTAnalyzer:
    """Cost-optimized GPT analyzer that uses concise prompts and real legal context."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-5')
        
        if not self.api_key or self.api_key in ['demo_key', 'demo_key_placeholder', 'your_gpt5_api_key_here']:
            raise ValueError("Please set a valid OPENAI_API_KEY in your environment variables or .env file")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def analyze_clause(self, clause_text: str, legal_context: Dict[str, List[Dict[str, Any]]], clause_id: int) -> ClauseAnalysis:
        """Analyze a single T&C clause with optimized, concise prompts."""
        
        # Create focused legal context - only most relevant paragraphs
        relevant_laws = []
        context_snippets = []
        
        # Get top 2 most relevant civil code paragraphs
        for item in legal_context.get('civil_code', [])[:2]:
            if item.get('similarity', 0) > 0.4:  # Only highly relevant
                law_ref = item.get('metadata', {}).get('paragraph', 'N/A')
                relevant_laws.append(f"§{law_ref} OZ")
                context_snippets.append(f"§{law_ref}: {item['text'][:100]}...")
        
        # Get top 1 most relevant criminal code paragraph
        for item in legal_context.get('criminal_code', [])[:1]:
            if item.get('similarity', 0) > 0.4:  # Only highly relevant
                law_ref = item.get('paragraph_number', 'N/A')
                relevant_laws.append(f"§{law_ref} TZ")
                context_snippets.append(f"§{law_ref}: {item['text'][:100]}...")
        
        # Create concise, focused prompt
        context_text = " | ".join(context_snippets) if context_snippets else "Obecné právní zásady"
        
        prompt = f"""Analyzuj klauzuli T&C podle českého práva:
KLAUZULE: "{clause_text}"
KONTEXT: {context_text}

Odpověz JSON:
{{"risk":"Low/Medium/High/Critical","summary":"krátké shrnutí","conflicts":["konflikty"],"explanation":"důvod rizika","laws":["{','.join(relevant_laws) if relevant_laws else 'obecné právo'}"]}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Právní expert. Odpovídej pouze JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_completion_tokens=400  # Reduced from 1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        analysis_data = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        analysis_data = self._create_fallback_analysis(clause_text)
                else:
                    analysis_data = self._create_fallback_analysis(clause_text)
            
            # Validate and clean data
            risk_level = analysis_data.get("risk", "Medium")
            if risk_level not in ["Low", "Medium", "High", "Critical"]:
                risk_level = "Medium"
            
            return ClauseAnalysis(
                clause_id=clause_id,
                original_text=clause_text,
                risk_level=RiskLevel(risk_level),
                summary=analysis_data.get("summary", "Analýza dokončena.")[:200],  # Limit length
                legal_conflicts=analysis_data.get("conflicts", [])[:3],  # Limit to 3
                explanation=analysis_data.get("explanation", "Standardní analýza.")[:300],  # Limit length
                relevant_laws=analysis_data.get("laws", relevant_laws)[:3]  # Limit to 3
            )
            
        except Exception as e:
            print(f"Error in optimized GPT analysis: {e}")
            return self._create_fallback_analysis_object(clause_text, clause_id, str(e))
    
    def _create_fallback_analysis(self, clause_text: str) -> dict:
        """Create fallback analysis data."""
        return {
            "risk": "Medium",
            "summary": "Vyžaduje přezkoumání.",
            "conflicts": ["Možné právní problémy"],
            "explanation": "Automatická analýza nebyla dokončena.",
            "laws": ["Obecné právní zásady"]
        }
    
    def _create_fallback_analysis_object(self, clause_text: str, clause_id: int, error_msg: str) -> ClauseAnalysis:
        """Create fallback ClauseAnalysis object."""
        return ClauseAnalysis(
            clause_id=clause_id,
            original_text=clause_text,
            risk_level=RiskLevel.MEDIUM,
            summary="Analýza nebyla dokončena kvůli chybě.",
            legal_conflicts=[],
            explanation=f"Chyba: {error_msg[:100]}",
            relevant_laws=[]
        )
    
    def generate_overall_summary(self, clause_analyses: List[ClauseAnalysis]) -> str:
        """Generate concise overall summary."""
        
        risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for analysis in clause_analyses:
            risk_counts[analysis.risk_level.value] += 1
        
        total = len(clause_analyses)
        high_risk = risk_counts['High'] + risk_counts['Critical']
        
        # Ultra-concise prompt for summary
        prompt = f"""Shrnutí analýzy {total} klauzulí T&C:
Vysoké riziko: {high_risk}
Střední riziko: {risk_counts['Medium']}
Nízké riziko: {risk_counts['Low']}

Vytvoř krátké shrnutí (max 100 slov):"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Právní expert. Stručné odpovědi."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=150  # Very limited for cost efficiency
            )
            
            return response.choices[0].message.content.strip()[:300]  # Limit length
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Analyzováno {total} klauzulí. Vysoké riziko: {high_risk}. Doporučuje se právní konzultace."