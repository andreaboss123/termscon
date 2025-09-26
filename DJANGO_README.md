# Django Terms & Conditions Analyzer

This Django version of the Terms & Conditions Analyzer provides a complete web application with database persistence and advanced features.

## Features

### Django Framework Benefits
- **Database Persistence**: All analyses are saved and can be reviewed later
- **History Management**: Browse through past analyses with detailed records
- **Admin Interface**: Django admin for data management
- **Session Management**: Built-in session handling
- **Scalability**: Production-ready Django architecture

### Core Functionality
- **Web Interface**: Clean, responsive HTML/CSS/JavaScript frontend
- **Document Analysis**: Intelligent clause segmentation and risk assessment  
- **Legal Context**: Integration with Czech Civil Code and Criminal Code databases
- **Risk Assessment**: 4-level system (Low, Medium, High, Critical)
- **Analysis History**: Permanent storage and retrieval of past analyses

## Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2.7

### Installation

1. Install Django dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations to set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Start the Django development server:
```bash
python manage.py runserver
```

4. Visit http://localhost:8000 in your browser

### Optional: Create Admin User
```bash
python manage.py createsuperuser
```
Then visit http://localhost:8000/admin to manage data.

## Usage

### Main Features
1. **Home Page**: Upload documents or paste text for analysis
2. **Analysis Results**: Real-time risk assessment with detailed explanations
3. **History Page**: View all past analyses with summary information
4. **Detail View**: Deep dive into specific analysis results

### API Endpoints
- `GET /`: Main analysis interface
- `POST /api/analyze/`: Submit document for analysis
- `GET /api/health/`: Health check
- `GET /history/`: Analysis history page  
- `GET /analysis/<uuid>/`: Detailed analysis view

## Database Schema

### AnalysisSession Model
- `id`: UUID primary key
- `created_at`: Timestamp
- `original_filename`: Uploaded file name
- `document_text`: Original document content
- `overall_risk_score`: Risk level (Low/Medium/High/Critical)
- `total_clauses`: Number of clauses analyzed
- `high_risk_count`: Count of high-risk clauses
- `medium_risk_count`: Count of medium-risk clauses  
- `low_risk_count`: Count of low-risk clauses
- `overview`: Summary text

### ClauseAnalysisResult Model
- `session`: Foreign key to AnalysisSession
- `clause_id`: Clause number
- `original_text`: Clause text
- `risk_level`: Risk assessment
- `summary`: Human-readable summary
- `legal_conflicts`: JSON array of conflicts
- `explanation`: Detailed explanation
- `relevant_laws`: JSON array of relevant laws

## Django App Structure

```
termscon_django/
├── settings.py          # Django configuration
├── urls.py             # Main URL routing
├── analyzer/           # Main Django app
│   ├── models.py       # Database models
│   ├── views.py        # Request handlers
│   ├── urls.py         # App URL routing
│   ├── apps.py         # App configuration
│   └── migrations/     # Database migrations
├── templates/analyzer/  # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   ├── history.html    # Analysis history
│   └── detail.html     # Analysis detail
└── manage.py           # Django management script
```

## Development

### Database Management
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Running Tests
```bash
# Run Django tests
python manage.py test

# Run custom analysis tests
python test_analysis.py
```

## Advantages over FastAPI Version

1. **Database Persistence**: Permanent storage of all analyses
2. **Admin Interface**: Built-in data management
3. **User Management**: Authentication system ready for production
4. **Template System**: Powerful Django template engine
5. **Migrations**: Database schema versioning
6. **Middleware**: Built-in security and session management
7. **Static Files**: Proper handling of CSS/JS/images
8. **Production Ready**: Built-in security features and deployment tools

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure allowed hosts
3. Set up database (PostgreSQL recommended)
4. Configure static files serving
5. Use WSGI server (gunicorn)
6. Set up reverse proxy (nginx)
7. Configure SSL/TLS

Example production settings:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'termscon',
        'USER': 'termscon_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```