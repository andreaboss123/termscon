#!/usr/bin/env python3

import sys
import os
import json
import uuid
from typing import Optional, List
import sqlite3
import hashlib

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/termscon/termscon')

from backend.models.simple_schemas import AnalysisResult, OverallSummary, RiskLevel
from backend.utils.text_processing_simple import SimpleTextProcessor

# Try to import real GPT analyzer, fallback to simple if OpenAI not configured
try:
    from backend.utils.gpt_analyzer_real import RealGPTAnalyzer
    USE_REAL_GPT = True
except ImportError:
    USE_REAL_GPT = False

from backend.utils.gpt_analyzer_simple import SimpleGPTAnalyzer

class SimplifiedVectorDB:
    def __init__(self, chroma_db_path: str, criminal_db_path: str):
        self.chroma_db_path = chroma_db_path
        self.criminal_db_path = criminal_db_path
    
    def get_legal_context(self, query_embedding: List[float], n_results: int = 3) -> dict:
        """Mock legal context retrieval."""
        # Mock some legal context
        civil_context = [
            {
                'text': '§1815 Občanského zákoníku: Smlouva je neplatná, pokud odporuje zákonu nebo dobrým mravům.',
                'metadata': {'paragraph': '1815'}
            },
            {
                'text': '§1826 Občanského zákoníku: Podmínky smlouvy musí být spravedlivé pro obě strany.',
                'metadata': {'paragraph': '1826'}
            }
        ]
        
        criminal_context = [
            {
                'paragraph_number': '1',
                'text': '§1 Trestního zákoníku: Čin je trestný, jen pokud jeho trestnost byla zákonem stanovena dříve.',
                'similarity': 0.7
            }
        ]
        
        return {
            'civil_code': civil_context,
            'criminal_code': criminal_context
        }

class SimpleApp:
    def __init__(self):
        self.vector_db = SimplifiedVectorDB(
            "/home/runner/work/termscon/termscon/chroma.sqlite3",
            "/home/runner/work/termscon/termscon/trestni_zakonik.sqlite"
        )
        self.text_processor = SimpleTextProcessor()
        
        # Try to use real GPT analyzer, fallback to mock if not configured
        if USE_REAL_GPT:
            try:
                self.gpt_analyzer = RealGPTAnalyzer()
                print("✅ Using real OpenAI GPT analyzer")
            except ValueError as e:
                print(f"⚠️  OpenAI API not configured: {e}")
                print("📝 Using mock analyzer instead. Set OPENAI_API_KEY environment variable to use real GPT analysis.")
                self.gpt_analyzer = SimpleGPTAnalyzer()
        else:
            self.gpt_analyzer = SimpleGPTAnalyzer()
    
    def analyze_text(self, text_content: str) -> AnalysisResult:
        """Analyze terms and conditions text."""
        
        if not text_content.strip():
            raise ValueError("No text content provided")
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Segment the document
        clauses = self.text_processor.segment_terms_conditions(text_content)
        
        if not clauses:
            raise ValueError("Could not segment document into clauses")
        
        # Analyze each clause
        clause_analyses = []
        
        for i, clause in enumerate(clauses):
            # Get mock embedding
            clause_embedding = self.text_processor.get_text_embedding_mock(clause)
            
            # Get legal context
            legal_context = self.vector_db.get_legal_context(clause_embedding)
            
            # Analyze with GPT (mock)
            analysis = self.gpt_analyzer.analyze_clause(clause, legal_context, i + 1)
            clause_analyses.append(analysis)
        
        # Calculate overall summary
        risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for analysis in clause_analyses:
            risk_counts[analysis.risk_level.value] += 1
        
        # Determine overall risk level
        if risk_counts["Critical"] > 0:
            overall_risk = RiskLevel.CRITICAL
        elif risk_counts["High"] > 0:
            overall_risk = RiskLevel.HIGH
        elif risk_counts["Medium"] > risk_counts["Low"]:
            overall_risk = RiskLevel.MEDIUM
        else:
            overall_risk = RiskLevel.LOW
        
        # Generate overall summary text
        overview_text = self.gpt_analyzer.generate_overall_summary(clause_analyses)
        
        overall_summary = OverallSummary(
            overall_risk_score=overall_risk,
            total_clauses=len(clause_analyses),
            high_risk_count=risk_counts["High"] + risk_counts["Critical"],
            medium_risk_count=risk_counts["Medium"],
            low_risk_count=risk_counts["Low"],
            overview=overview_text
        )
        
        return AnalysisResult(
            document_id=document_id,
            overall_summary=overall_summary,
            clause_analyses=clause_analyses
        )

def main():
    """Main function for testing the application."""
    
    # Sample Terms & Conditions text for testing
    sample_tc = """
    1. Uživatelské podmínky
    Tyto podmínky se vztahují na všechny uživatele naší služby. Vyhrazujeme si právo kdykoli změnit tyto podmínky bez předchozího upozornění.
    
    2. Odpovědnost
    Společnost se zprošťuje veškeré odpovědnosti za škody způsobené užíváním služby. Uživatel používá službu na vlastní riziko.
    
    3. Ochrana dat
    Vaše osobní údaje zpracováváme v souladu s GDPR. Snažíme se zajistit maximální bezpečnost vašich dat.
    
    4. Ukončení služby
    Službu můžeme kdykoli ukončit podle našeho uvážení. V případě ukončení nebudou vráceny žádné poplatky.
    """
    
    print("=== Terms & Conditions Analyzer Demo ===")
    print("\nAnalyzuji vzorové obchodní podmínky...")
    
    app = SimpleApp()
    
    try:
        result = app.analyze_text(sample_tc)
        
        print(f"\n📄 Dokument ID: {result.document_id}")
        print(f"🔍 Celkem klauzulí: {result.overall_summary.total_clauses}")
        print(f"⚠️  Celkové riziko: {result.overall_summary.overall_risk_score.value}")
        print(f"🚨 Vysoké riziko: {result.overall_summary.high_risk_count}")
        print(f"⚡ Střední riziko: {result.overall_summary.medium_risk_count}")
        print(f"✅ Nízké riziko: {result.overall_summary.low_risk_count}")
        
        print(f"\n📋 Celkové shrnutí:")
        print(result.overall_summary.overview)
        
        print(f"\n📝 Detailní analýza klauzulí:")
        
        for analysis in result.clause_analyses:
            print(f"\n--- Klauzule {analysis.clause_id} ---")
            print(f"🎯 Riziko: {analysis.risk_level.value}")
            print(f"📄 Text: {analysis.original_text[:100]}...")
            print(f"💡 Shrnutí: {analysis.summary}")
            if analysis.legal_conflicts:
                print(f"⚖️  Právní konflikty: {', '.join(analysis.legal_conflicts)}")
            if analysis.relevant_laws:
                print(f"📚 Relevantní právo: {', '.join(analysis.relevant_laws)}")
            print(f"🔍 Vysvětlení: {analysis.explanation}")
        
        print("\n=== Analýza dokončena ===")
        
    except Exception as e:
        print(f"❌ Chyba při analýze: {str(e)}")

if __name__ == "__main__":
    main()