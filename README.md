# Terms & Conditions Analyzer (TermsCon)

A comprehensive web application that analyzes Terms & Conditions documents against Czech legal frameworks to identify potentially unfair, problematic, or illegal clauses.

## Features

🔍 **Intelligent Analysis**: Automatically segments T&C documents into individual clauses for detailed analysis

⚖️ **Legal Framework Integration**: Leverages pre-embedded Czech Civil Code and Criminal Code for legal context

🤖 **AI-Powered Assessment**: Uses GPT-5 API (with fallback mock analysis) for risk assessment and legal conflict detection

📊 **Interactive Dashboard**: User-friendly web interface with color-coded risk levels and detailed explanations

📄 **Multiple Input Methods**: Supports text paste and file upload (TXT format in current demo)

## Risk Assessment Levels

- **🟢 Low**: Standard clauses without legal problems
- **🟡 Medium**: Potentially problematic clauses requiring attention  
- **🔴 High**: Likely invalid or unfair clauses
- **🟣 Critical**: Clauses clearly in conflict with legal requirements

## Quick Start

### Prerequisites
- Python 3.8+
- Required packages (see requirements.txt)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/andreaboss123/termscon.git
cd termscon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env to add your GPT-5 API key
```

### Running the Application

#### Command Line Demo
```bash
python main.py
```

#### Web Application
```bash
python web_app.py
```
Then open http://localhost:8000 in your browser.

## Usage

### Web Interface
1. Visit http://localhost:8000
2. Either paste T&C text or upload a text file
3. Click "Analyzovat podmínky" (Analyze Terms)
4. Review the detailed analysis with risk assessments and legal explanations

### Command Line
The CLI version analyzes sample terms and conditions and outputs detailed results to the terminal.

## Architecture

### Backend Components
- **Text Processing**: Segments documents into analyzable clauses
- **Vector Database**: Queries pre-embedded Czech legal codes for relevant context
- **GPT Analysis**: Performs risk assessment and legal conflict detection
- **API Endpoints**: FastAPI-based REST API for web interface

### Database Structure
- `chroma.sqlite3`: ChromaDB with embedded Civil Code (1536-dimensional vectors)
- `trestni_zakonik.sqlite`: SQLite with Criminal Code paragraphs and embeddings

### Frontend
- Modern responsive web interface
- Real-time analysis with loading indicators
- Interactive results with color-coded risk levels
- Detailed clause-by-clause breakdown

## API Endpoints

- `GET /`: Main web interface
- `POST /api/analyze`: Analyze T&C document (form-data with text_content or file)
- `GET /api/health`: Health check

## Example Analysis Output

```
📊 Výsledky analýzy
Celkem klauzulí: 4
Vysoké riziko: 1
Celkové hodnocení: Vysoké riziko

Klauzule 1 - Vysoké riziko
💡 Shrnutí: Klauzule je jednostranně nevýhodná a může být problematická z právního hlediska.
⚖️ Právní konflikty: Nerovnováha v právech stran  
📚 Relevantní právo: §1826 Občanského zákoníku
🔍 Vysvětlení: Tato klauzule dává službě značnou volnost při změnách podmínek...
```

## Legal Context

The application analyzes clauses against:
- **Czech Civil Code**: Consumer protection, contract law, unfair terms
- **Czech Criminal Code**: Potential criminal violations in T&C clauses

## Development

### Project Structure
```
termscon/
├── backend/
│   ├── app/           # FastAPI application
│   ├── database/      # Vector database connections  
│   ├── models/        # Data models and schemas
│   └── utils/         # Text processing and analysis utilities
├── main.py            # CLI demo application
├── web_app.py         # Web application server
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

### Adding New Features
- Extend `SimpleGPTAnalyzer` for additional analysis capabilities
- Modify `SimpleTextProcessor` for better clause segmentation
- Add new risk assessment criteria in the analysis logic

## Limitations (Demo Version)

- **Mock Analysis**: Uses pattern-based analysis instead of real GPT-5 integration
- **File Support**: Currently limited to .txt files (PDF/DOCX extraction disabled)
- **Language**: Optimized for Czech legal framework and language
- **Vector Search**: Simplified mock implementation for legal context retrieval

## Production Deployment

For production use:
1. Add real GPT-5 API integration
2. Enable full document format support (PDF, DOCX)
3. Implement proper vector similarity search
4. Add user authentication and session management
5. Deploy with proper WSGI server (gunicorn) and reverse proxy (nginx)

## License

This project is developed for legal analysis purposes. Ensure compliance with local laws and API terms of service when deploying.