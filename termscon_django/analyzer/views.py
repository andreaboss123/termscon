import sys
import os
import json
from typing import List
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import uuid

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/termscon/termscon')

from .simple_schemas import AnalysisResult, OverallSummary, RiskLevel
from .text_processing_simple import SimpleTextProcessor  
from .vector_db_real import RealVectorDB
from .models import AnalysisSession, ClauseAnalysisResult

# Try to use optimized GPT analyzer first
try:
    from .gpt_analyzer_optimized import OptimizedGPTAnalyzer
    USE_OPTIMIZED_GPT = True
except ImportError:
    from .gpt_analyzer_real import RealGPTAnalyzer
    USE_OPTIMIZED_GPT = False


class SimplifiedVectorDB:
    def __init__(self, chroma_db_path: str, criminal_db_path: str):
        # Use the real vector DB for actual embedding search
        self.real_db = RealVectorDB(chroma_db_path, criminal_db_path)
    
    def get_legal_context(self, query_text: str, n_results: int = 3) -> dict:
        """Get legal context using real embeddings."""
        return self.real_db.get_legal_context(query_text, n_results)


class TermsAnalyzer:
    def __init__(self):
        chroma_db_path = "/home/runner/work/termscon/termscon/chroma.sqlite3"
        criminal_db_path = "/home/runner/work/termscon/termscon/trestni_zakonik.sqlite"
        
        self.vector_db = SimplifiedVectorDB(chroma_db_path, criminal_db_path)
        self.text_processor = SimpleTextProcessor()
        
        # Try to use optimized GPT analyzer, fallback to regular, then mock
        if USE_OPTIMIZED_GPT:
            try:
                self.gpt_analyzer = OptimizedGPTAnalyzer()
                print("✅ Using optimized OpenAI GPT analyzer (cost-efficient)")
            except ValueError as e:
                print(f"⚠️  OpenAI API not configured: {e}")
                print("📝 Using mock analyzer instead. Set OPENAI_API_KEY environment variable to use real GPT analysis.")
                from .gpt_analyzer_simple import SimpleGPTAnalyzer
                self.gpt_analyzer = SimpleGPTAnalyzer()
        else:
            try:
                self.gpt_analyzer = RealGPTAnalyzer()
                print("✅ Using standard OpenAI GPT analyzer")
            except ValueError as e:
                print(f"⚠️  OpenAI API not configured: {e}")
                print("📝 Using mock analyzer instead. Set OPENAI_API_KEY environment variable to use real GPT analysis.")
                from .gpt_analyzer_simple import SimpleGPTAnalyzer
                self.gpt_analyzer = SimpleGPTAnalyzer()
    
    def analyze_text(self, text_content: str, filename: str = None) -> AnalysisResult:
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
            print(f"Analyzing clause {i+1}/{len(clauses)}")
            
            # Get relevant legal context using semantic search on actual clause text
            legal_context = self.vector_db.get_legal_context(clause, n_results=3)
            
            # Analyze with GPT (optimized version)
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
        
        result = AnalysisResult(
            document_id=document_id,
            overall_summary=overall_summary,
            clause_analyses=clause_analyses
        )
        
        # Save to database
        self._save_to_database(result, text_content, filename)
        
        return result
    
    def _save_to_database(self, result: AnalysisResult, text_content: str, filename: str = None):
        """Save analysis result to database."""
        try:
            session = AnalysisSession.objects.create(
                id=result.document_id,
                original_filename=filename or "pasted_text.txt",
                document_text=text_content,
                overall_risk_score=result.overall_summary.overall_risk_score.value,
                total_clauses=result.overall_summary.total_clauses,
                high_risk_count=result.overall_summary.high_risk_count,
                medium_risk_count=result.overall_summary.medium_risk_count,
                low_risk_count=result.overall_summary.low_risk_count,
                overview=result.overall_summary.overview
            )
            
            for clause_analysis in result.clause_analyses:
                ClauseAnalysisResult.objects.create(
                    session=session,
                    clause_id=clause_analysis.clause_id,
                    original_text=clause_analysis.original_text,
                    risk_level=clause_analysis.risk_level.value,
                    summary=clause_analysis.summary,
                    legal_conflicts=clause_analysis.legal_conflicts,
                    explanation=clause_analysis.explanation,
                    relevant_laws=clause_analysis.relevant_laws
                )
        except Exception as e:
            print(f"Error saving to database: {e}")


# Initialize analyzer instance
analyzer = TermsAnalyzer()


def home(request):
    """Render the main page."""
    return render(request, 'analyzer/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def analyze_document(request):
    """Analyze T&C document from file upload or text input."""
    
    try:
        text_content = None
        filename = None
        
        # Check if it's a file upload
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            filename = uploaded_file.name
            
            if filename.lower().endswith('.txt'):
                text_content = uploaded_file.read().decode('utf-8')
            else:
                return JsonResponse({'error': 'Only .txt files are supported in demo'}, status=400)
        
        # Check if it's text content
        elif 'text_content' in request.POST:
            text_content = request.POST['text_content']
            filename = "pasted_text.txt"
        
        else:
            return JsonResponse({'error': 'Either file or text_content must be provided'}, status=400)
        
        if not text_content or not text_content.strip():
            return JsonResponse({'error': 'No text content found in the document'}, status=400)
        
        # Analyze the document
        result = analyzer.analyze_text(text_content, filename)
        
        # Convert to dict for JSON response
        response_data = {
            "document_id": result.document_id,
            "overall_summary": {
                "overall_risk_score": result.overall_summary.overall_risk_score.value,
                "total_clauses": result.overall_summary.total_clauses,
                "high_risk_count": result.overall_summary.high_risk_count,
                "medium_risk_count": result.overall_summary.medium_risk_count,
                "low_risk_count": result.overall_summary.low_risk_count,
                "overview": result.overall_summary.overview
            },
            "clause_analyses": [
                {
                    "clause_id": clause.clause_id,
                    "original_text": clause.original_text,
                    "risk_level": clause.risk_level.value,
                    "summary": clause.summary,
                    "legal_conflicts": clause.legal_conflicts,
                    "explanation": clause.explanation,
                    "relevant_laws": clause.relevant_laws
                }
                for clause in result.clause_analyses
            ]
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return JsonResponse({'error': f'Analysis failed: {str(e)}'}, status=500)


def health_check(request):
    """Health check endpoint."""
    return JsonResponse({"status": "healthy", "message": "Terms & Conditions Analyzer is running"})


def analysis_history(request):
    """View analysis history."""
    sessions = AnalysisSession.objects.all()[:20]  # Last 20 sessions
    return render(request, 'analyzer/history.html', {'sessions': sessions})


def analysis_detail(request, session_id):
    """View detailed analysis results."""
    try:
        session = AnalysisSession.objects.get(id=session_id)
        clauses = session.clauses.all()
        return render(request, 'analyzer/detail.html', {
            'session': session,
            'clauses': clauses
        })
    except AnalysisSession.DoesNotExist:
        return HttpResponse("Analysis not found", status=404)
