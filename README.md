# Terms & Conditions Analyzer (TermsCon)

A comprehensive web application that analyzes Terms & Conditions documents against Czech legal frameworks to identify potentially unfair, problematic, or illegal clauses.

## Available Implementations

🔥 **NEW: Django Version** - Full-featured web application with database persistence
📋 **Legacy: FastAPI Version** - Simple API-based implementation

## Django Version (Recommended)

The Django implementation provides a complete web application with database persistence, user interface, and advanced features.

### Quick Start (Django)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Start server
python manage.py runserver

# Visit http://localhost:8000
```

**Features:**
- 📊 **Database Persistence**: All analyses saved permanently
- 📋 **Analysis History**: Browse and review past analyses
- 🎯 **Advanced UI**: Clean, responsive web interface
- ⚖️ **Legal Integration**: Czech Civil Code and Criminal Code analysis
- 🔒 **Production Ready**: Django framework with security features

See [DJANGO_README.md](DJANGO_README.md) for detailed Django-specific documentation.

## Legacy FastAPI Version

The original FastAPI implementation provides a simple API-based approach.

### Quick Start (FastAPI)
```bash
python web_app.py
# Visit http://localhost:8000
```

## Core Features (Both Versions)

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

## Project Structure

```
termscon/
├── termscon_django/          # Django web application (RECOMMENDED)
│   ├── analyzer/            # Main Django app
│   ├── settings.py          # Django configuration
│   └── manage.py           # Django management
├── templates/              # HTML templates
├── backend/               # Shared analysis logic
│   ├── models/           # Data models
│   └── utils/            # Text processing & analysis
├── main.py               # CLI demo application
├── web_app.py            # Legacy FastAPI application
├── requirements.txt      # Dependencies
├── README.md            # This file
└── DJANGO_README.md     # Django-specific documentation
```

## Testing

Both implementations include comprehensive testing:

```bash
# Test core analysis functionality
python test_analysis.py

# Django-specific tests
python manage.py test
```

## Database Structure (Django Version)

The Django version includes persistent storage:
- **AnalysisSession**: Stores overall analysis results
- **ClauseAnalysisResult**: Stores individual clause analyses
- Built-in Django admin interface for data management

## API Endpoints

### Django Version
- `GET /`: Main web interface
- `POST /api/analyze/`: Analyze document
- `GET /history/`: Analysis history
- `GET /analysis/<uuid>/`: Detailed analysis view
- `GET /admin/`: Django admin interface

### FastAPI Version (Legacy)
- `GET /`: Web interface
- `POST /api/analyze`: Analyze document
- `GET /api/health`: Health check

## Limitations (Demo Version)

- **Mock Analysis**: Uses pattern-based analysis instead of real GPT-5 integration
- **File Support**: Currently limited to .txt files (PDF/DOCX extraction disabled)
- **Language**: Optimized for Czech legal framework and language
- **Vector Search**: Simplified mock implementation for legal context retrieval

## Production Deployment

### Django Version (Recommended)
```bash
# Set up production database
python manage.py migrate --settings=production_settings

# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn termscon_django.wsgi:application
```

### FastAPI Version
```bash
# Run with uvicorn
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

For production use:
1. Add real GPT-5 API integration
2. Enable full document format support (PDF, DOCX)
3. Implement proper vector similarity search
4. Add user authentication and session management
5. Deploy with proper WSGI server (gunicorn) and reverse proxy (nginx)

## License

This project is developed for legal analysis purposes. Ensure compliance with local laws and API terms of service when deploying.