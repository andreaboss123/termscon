# OpenAI API Integration Guide

The Terms & Conditions Analyzer now supports real OpenAI GPT analysis for more accurate and sophisticated legal analysis.

## Setup Instructions

### 1. Get OpenAI API Key

1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to API Keys section
3. Create a new API key
4. Copy the API key (starts with `sk-...`)

### 2. Configure Environment Variables

Create a `.env` file in the project root or set environment variables:

```bash
# Option 1: Create .env file
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env
echo "OPENAI_MODEL=gpt-4" >> .env

# Option 2: Export environment variables
export OPENAI_API_KEY=sk-your-actual-api-key-here
export OPENAI_MODEL=gpt-4
```

### 3. Available Models

- `gpt-4` (recommended for best analysis quality)
- `gpt-3.5-turbo` (faster and cheaper alternative)
- `gpt-4-turbo` (if available in your region)

## How It Works

### Real vs Mock Analysis

**With Valid API Key:**
- ✅ Real GPT analysis of legal clauses
- ✅ Context-aware risk assessment
- ✅ Detailed legal explanations in Czech
- ✅ Specific law citations
- ✅ Professional legal summaries

**Without API Key (Fallback):**
- 📝 Pattern-based mock analysis
- 📝 Keyword detection for risk levels
- 📝 Generic legal explanations
- 📝 Standard law references

### Analysis Process

1. **Text Segmentation**: Document split into individual clauses
2. **Legal Context**: Relevant Czech Civil/Criminal Code sections retrieved
3. **GPT Analysis**: Each clause analyzed against legal framework
4. **Risk Assessment**: 4-level risk categorization (Low/Medium/High/Critical)
5. **Summary Generation**: Overall document risk assessment

### API Usage and Costs

**Estimated Costs (GPT-4):**
- Small T&C (1-5 clauses): ~$0.01-0.05
- Medium T&C (5-15 clauses): ~$0.05-0.15  
- Large T&C (15+ clauses): ~$0.15-0.50

**Token Usage:**
- Input: ~500-1000 tokens per clause (context + prompt)
- Output: ~200-400 tokens per clause (analysis response)

## Testing the Integration

### Django Web Application

```bash
# Set your API key
export OPENAI_API_KEY=sk-your-actual-key

# Start Django server
python manage.py runserver

# Visit http://localhost:8000
# Upload T&C document or paste text
# Click "Analyzovat podmínky"
```

### Command Line Interface

```bash
# Set your API key
export OPENAI_API_KEY=sk-your-actual-key

# Run CLI version
python main.py
```

## Error Handling

The system includes robust error handling:

- **Invalid API Key**: Falls back to mock analysis
- **API Rate Limits**: Implements retry logic
- **Network Issues**: Graceful degradation
- **JSON Parsing Errors**: Fallback responses
- **Model Unavailable**: Alternative model selection

## Example Output

### With OpenAI API:
```
🎯 Riziko: High
💡 Shrnutí: Tato klauzule umožňuje společnosti jednostranně měnit podmínky bez souhlasu uživatele, což může porušovat práva spotřebitele podle §1826 Občanského zákoníku.
⚖️ Právní konflikty: Nerovnováha smluvních práv, Možné porušení spotřebitelských práv
📚 Relevantní právo: §1826 Občanského zákoníku, §52 Zákona o ochraně spotřebitele
🔍 Vysvětlení: Klauzule porušuje zásadu rovnováhy smluvních stran tím, že umožňuje jednostranné změny...
```

### Without API Key (Mock):
```
🎯 Riziko: High  
💡 Shrnutí: Klauzule je jednostranně nevýhodná a může být problematická z právního hlediska.
⚖️ Právní konflikty: Nerovnováha v právech stran
📚 Relevantní právo: §1826 Občanského zákoníku
🔍 Vysvětlení: Tato klauzule dává službě značnou volnost při změnách podmínek...
```

## Security Notes

- Never commit API keys to version control
- Use environment variables or secure vault systems
- Consider API key rotation in production
- Monitor API usage and set billing limits
- Use least-privilege API keys (no fine-tuning/admin access)

## Production Deployment

For production environments:

```bash
# Use secure environment variable management
# Example with Docker:
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY termscon-app

# Example with systemd:
Environment=OPENAI_API_KEY=sk-your-key
```

## Troubleshooting

### Common Issues

**"Connection error" messages:**
- Check internet connectivity
- Verify API key is valid
- Check OpenAI service status

**"Rate limit exceeded":**
- Reduce analysis frequency
- Upgrade OpenAI plan
- Implement request queuing

**"Model not available":**
- Switch to gpt-3.5-turbo
- Check regional availability
- Verify API access level

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed API request/response information for troubleshooting.