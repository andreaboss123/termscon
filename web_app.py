#!/usr/bin/env python3

import sys
import os
import json
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/termscon/termscon')

from main import SimpleApp

app = FastAPI(title="Terms & Conditions Analyzer", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the analyzer
analyzer_app = SimpleApp()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analýza obchodních podmínek</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 2px dashed #3498db;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 20px;
                transition: background-color 0.3s;
            }
            .upload-area:hover {
                background-color: #ecf0f1;
            }
            textarea {
                width: 100%;
                height: 200px;
                margin: 10px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-family: inherit;
                resize: vertical;
            }
            button {
                background-color: #3498db;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 5px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #2980b9;
            }
            button:disabled {
                background-color: #bdc3c7;
                cursor: not-allowed;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                display: none;
            }
            .risk-badge {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 0.8em;
            }
            .risk-low { background-color: #27ae60; }
            .risk-medium { background-color: #f39c12; }
            .risk-high { background-color: #e74c3c; }
            .risk-critical { background-color: #8e44ad; }
            .clause {
                margin: 20px 0;
                padding: 15px;
                border-left: 4px solid #3498db;
                background: white;
                border-radius: 0 5px 5px 0;
            }
            .clause.high-risk { border-left-color: #e74c3c; }
            .clause.medium-risk { border-left-color: #f39c12; }
            .clause.low-risk { border-left-color: #27ae60; }
            .clause.critical-risk { border-left-color: #8e44ad; }
            .summary-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #e0e0e0;
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
            }
            .loader {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
                display: none;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Analýza obchodních podmínek</h1>
            
            <div class="upload-area">
                <p><strong>Vložte text obchodních podmínek</strong></p>
                <textarea id="textInput" placeholder="Vložte zde text obchodních podmínek, které chcete analyzovat..."></textarea>
                <p>nebo</p>
                <input type="file" id="fileInput" accept=".txt,.pdf,.docx" style="margin: 10px;">
            </div>
            
            <div style="text-align: center;">
                <button onclick="analyzeText()">🔍 Analyzovat podmínky</button>
                <button onclick="loadSample()">📄 Načíst vzorové podmínky</button>
            </div>
            
            <div class="loader" id="loader"></div>
            
            <div class="results" id="results">
                <h2>📊 Výsledky analýzy</h2>
                <div id="resultsContent"></div>
            </div>
        </div>

        <script>
            function loadSample() {
                document.getElementById('textInput').value = `1. Uživatelské podmínky
Tyto podmínky se vztahují na všechny uživatele naší služby. Vyhrazujeme si právo kdykoli změnit tyto podmínky bez předchozího upozornění.

2. Odpovědnost
Společnost se zprošťuje veškeré odpovědnosti za škody způsobené užíváním služby. Uživatel používá službu na vlastní riziko.

3. Ochrana dat
Vaše osobní údaje zpracováváme v souladu s GDPR. Snažíme se zajistit maximální bezpečnost vašich dat.

4. Ukončení služby
Službu můžeme kdykoli ukončit podle našeho uvážení. V případě ukončení nebudou vráceny žádné poplatky.`;
            }

            function getRiskBadge(riskLevel) {
                const classes = {
                    'Low': 'risk-low',
                    'Medium': 'risk-medium', 
                    'High': 'risk-high',
                    'Critical': 'risk-critical'
                };
                const labels = {
                    'Low': 'Nízké',
                    'Medium': 'Střední',
                    'High': 'Vysoké', 
                    'Critical': 'Kritické'
                };
                return `<span class="risk-badge ${classes[riskLevel]}">${labels[riskLevel]} riziko</span>`;
            }

            async function analyzeText() {
                const textInput = document.getElementById('textInput');
                const fileInput = document.getElementById('fileInput');
                const loader = document.getElementById('loader');
                const results = document.getElementById('results');
                
                let textContent = textInput.value.trim();
                
                if (!textContent && !fileInput.files.length) {
                    alert('Prosím vložte text nebo vyberte soubor k analýze.');
                    return;
                }
                
                loader.style.display = 'block';
                results.style.display = 'none';
                
                try {
                    const formData = new FormData();
                    
                    if (fileInput.files.length > 0) {
                        formData.append('file', fileInput.files[0]);
                    } else {
                        formData.append('text_content', textContent);
                    }
                    
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    displayResults(data);
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Chyba při analýze: ' + error.message);
                } finally {
                    loader.style.display = 'none';
                }
            }
            
            function displayResults(data) {
                const resultsContent = document.getElementById('resultsContent');
                const results = document.getElementById('results');
                
                const summary = data.overall_summary;
                
                let html = `
                    <div class="summary-stats">
                        <div class="stat-card">
                            <div class="stat-number">${summary.total_clauses}</div>
                            <div>Celkem klauzulí</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${summary.high_risk_count}</div>
                            <div>Vysoké riziko</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${summary.medium_risk_count}</div>
                            <div>Střední riziko</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${summary.low_risk_count}</div>
                            <div>Nízké riziko</div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <h3>Celkové hodnocení: ${getRiskBadge(summary.overall_risk_score)}</h3>
                        <p><strong>${summary.overview}</strong></p>
                    </div>
                    
                    <h3>📋 Detailní analýza klauzulí</h3>
                `;
                
                data.clause_analyses.forEach(clause => {
                    const riskClass = clause.risk_level.toLowerCase() + '-risk';
                    html += `
                        <div class="clause ${riskClass}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <strong>Klauzule ${clause.clause_id}</strong>
                                ${getRiskBadge(clause.risk_level)}
                            </div>
                            <p><strong>Text:</strong> ${clause.original_text.length > 200 ? clause.original_text.substring(0, 200) + '...' : clause.original_text}</p>
                            <p><strong>💡 Shrnutí:</strong> ${clause.summary}</p>
                            <p><strong>🔍 Vysvětlení:</strong> ${clause.explanation}</p>
                            ${clause.legal_conflicts.length > 0 ? `<p><strong>⚖️ Právní konflikty:</strong> ${clause.legal_conflicts.join(', ')}</p>` : ''}
                            ${clause.relevant_laws.length > 0 ? `<p><strong>📚 Relevantní právní předpisy:</strong> ${clause.relevant_laws.join(', ')}</p>` : ''}
                        </div>
                    `;
                });
                
                resultsContent.innerHTML = html;
                results.style.display = 'block';
                results.scrollIntoView({ behavior: 'smooth' });
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/analyze")
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
            # For now, only handle text files in the demo
            if file.filename.lower().endswith('.txt'):
                document_text = content.decode('utf-8')
            else:
                raise HTTPException(status_code=400, detail="Only .txt files are supported in demo")
            
        elif text_content:
            document_text = text_content
        else:
            raise HTTPException(status_code=400, detail="Either file or text_content must be provided")
        
        if not document_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in the document")
        
        # Analyze the document
        result = analyzer_app.analyze_text(document_text)
        
        # Convert to dict for JSON response
        return {
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