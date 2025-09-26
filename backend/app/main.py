from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from typing import Optional
import sys
sys.path.append('/home/runner/work/termscon/termscon')

from backend.models.schemas import AnalysisResult, DocumentUpload, OverallSummary, RiskLevel
from backend.database.vector_db import VectorDatabase
from backend.utils.text_extraction import extract_text_from_file
from backend.utils.text_processing import TextProcessor
from backend.utils.gpt_analyzer import GPTAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Terms & Conditions Analyzer", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
chroma_db_path = "/home/runner/work/termscon/termscon/chroma.sqlite3"
criminal_db_path = "/home/runner/work/termscon/termscon/trestni_zakonik.sqlite"

vector_db = VectorDatabase(chroma_db_path, criminal_db_path)
text_processor = TextProcessor()
gpt_analyzer = GPTAnalyzer()

# Serve static files for frontend
if os.path.exists("/home/runner/work/termscon/termscon/frontend/build"):
    app.mount("/static", StaticFiles(directory="/home/runner/work/termscon/termscon/frontend/build/static"), name="static")

@app.get("/")
async def root():
    """Serve the frontend application."""
    frontend_path = "/home/runner/work/termscon/termscon/frontend/build/index.html"
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Terms & Conditions Analyzer API", "version": "1.0.0"}

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None)
):
    """Analyze T&C document from file upload or text input."""
    
    try:
        # Extract text content
        if file:
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            content = await file.read()
            document_text = extract_text_from_file(content, file.filename)
            filename = file.filename
        elif text_content:
            document_text = text_content
            filename = "pasted_text.txt"
        else:
            raise HTTPException(status_code=400, detail="Either file or text_content must be provided")
        
        if not document_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in the document")
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Segment the document into clauses
        clauses = text_processor.segment_terms_conditions(document_text)
        
        if not clauses:
            raise HTTPException(status_code=400, detail="Could not segment document into clauses")
        
        # Analyze each clause
        clause_analyses = []
        
        for i, clause in enumerate(clauses):
            # Get embedding for the clause
            clause_embedding = text_processor.get_text_embedding(clause)
            
            if not clause_embedding:
                continue
            
            # Get legal context
            legal_context = vector_db.get_legal_context(clause_embedding)
            
            # Analyze with GPT
            analysis = gpt_analyzer.analyze_clause(clause, legal_context, i + 1)
            clause_analyses.append(analysis)
        
        if not clause_analyses:
            raise HTTPException(status_code=500, detail="Could not analyze any clauses")
        
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
        overview_text = gpt_analyzer.generate_overall_summary(clause_analyses)
        
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
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Terms & Conditions Analyzer is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)