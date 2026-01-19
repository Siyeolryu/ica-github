# Health Supplement Review Fact-Check Engine

A system that quantitatively evaluates the reliability of health supplement reviews and provides professional analysis through an AI pharmacist persona.

## Key Features

### 1. Reliability Verification Engine (`core/validator.py`)
- **13-step advertising detection checklist** based automatic verification
- **Reliability score calculation**: `S = (L×0.2) + (R×0.2) + (M×0.3) + (P×0.1) + (C×0.2)`
- **Penalty system**: -10 points per item, flagged as advertisement if score < 40 or 3+ penalties

### 2. AI Pharmacist Analysis Engine (`core/analyzer.py`)
- **Persona**: 15-year experienced clinical pharmacist
- **AI Model**: Anthropic Claude Sonnet 4.5
- **Output**: JSON format (summary, efficacy, side effects, reliability, advice)
- **Hallucination prevention**: Only extracts evidence from review original text

## Installation

```bash
# 1. Clone repository
git clone https://github.com/Siyeolryu/ica-github.git
cd ica-github/dev2-2Hour/dev2-main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create .env file and add the following content
```

### Environment Variables Setup (.env file)

Create a `.env` file in the project root and add the following:

```env
# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Supabase Configuration
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

**How to get Supabase keys:**
1. Access [Supabase Dashboard](https://supabase.com/dashboard)
2. Select project → Settings → API
3. **Project URL**: Enter in `SUPABASE_URL`
4. **anon/public key**: Enter in `SUPABASE_ANON_KEY`
5. **service_role key**: Enter in `SUPABASE_SERVICE_ROLE_KEY` (admin privileges)

## Usage

### Basic Usage Example

```python
from core import validate_review, analyze_review

# 1. Reliability verification
review_text = "I've been using this product for a month and it's been effective..."

result = validate_review(
    review_text=review_text,
    length_score=70,      # Review length score (0-100)
    repurchase_score=80,  # Repurchase intention score (0-100)
    monthly_use_score=100, # One month usage (0-100)
    photo_score=50,       # Photo attachment score (0-100)
    consistency_score=85  # Content consistency score (0-100)
)

print(f"Reliability score: {result['trust_score']}")
print(f"Is advertisement: {result['is_ad']}")
print(f"Penalty reasons: {result['reasons']}")

# 2. AI Pharmacist Analysis (only for non-ad reviews)
if not result['is_ad']:
    ai_result = analyze_review(review_text)
    print(f"Summary: {ai_result['Summary']}")
    print(f"Efficacy: {ai_result['Efficacy']}")
    print(f"Side effects: {ai_result['Side_effects']}")
    print(f"Advice: {ai_result['Tip']}")
```

### Run Example

```bash
python example.py
```

## Project Structure

```
dev2-main/
├── core/                   # Core modules
│   ├── __init__.py
│   ├── validator.py        # Reliability verification engine
│   └── analyzer.py         # AI pharmacist analysis engine
├── database/               # Database modules
│   ├── __init__.py
│   ├── supabase_client.py  # Supabase client
│   └── test_connection.py  # Connection test script
├── logic_designer/         # Logic design modules
│   ├── __init__.py
│   ├── checklist.py        # 13-step checklist
│   ├── trust_score.py      # Reliability score calculation
│   └── analyzer.py         # AI analysis engine
├── ui_integration/         # Streamlit UI integration
│   ├── app.py              # Main Streamlit application
│   ├── supabase_data.py    # Supabase data manager
│   └── visualizations.py   # Chart visualization components
├── logs/                   # Development logs
│   ├── dev_log.md          # Development diary
│   ├── prompt_log.md       # Prompt design log
│   └── output_review.md    # Output review
├── example.py              # Usage example
├── requirements.txt        # Dependency packages
├── .env                    # Environment variables (gitignore)
├── SPEC.md                 # Project specification
├── CLAUDE.md               # AI work instructions
└── README.md               # Project documentation
```

## 13-Step Advertising Detection Checklist

1. Compensation statement presence
2. Excessive exclamation marks
3. Structured paragraph format
4. Lack of personal experience
5. Ingredient feature listing
6. Keyword repetition
7. Avoidance of drawbacks
8. Praise-focused composition
9. Misuse of technical terms
10. Unrealistic effect emphasis
11. Competitor product comparison
12. Promotional blog writing style
13. Excessive emoji usage

## Reliability Score Calculation Formula

```
S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)
```

- **L** (Length): Review length score
- **R** (Repurchase): Repurchase intention score
- **M** (Monthly Use): One month+ usage score
- **P** (Photo): Photo attachment score
- **C** (Consistency): Content consistency score

## AI Analysis Output Format

```json
{
  "Summary": "One-line review summary",
  "Efficacy": ["Efficacy 1", "Efficacy 2"],
  "Side_effects": ["Side effect 1", "Side effect 2"],
  "Trust_score": 85,
  "Tip": "Pharmacist's key advice",
  "disclaimer": "This analysis is based on actual user experience, not medical diagnosis."
}
```

## Tech Stack

- **Language**: Python 3.8+
- **AI Model**: Anthropic Claude Sonnet 4.5
- **Database**: Supabase (PostgreSQL)
- **Key Libraries**: anthropic, python-dotenv, supabase, streamlit, plotly

## Supabase Database Integration

### Connection Test

```bash
# Test Supabase connection
python database/test_connection.py
```

### Usage in Python

```python
from database import get_supabase_client, test_connection

# Test connection
if test_connection():
    print("✅ Supabase connection successful!")
    
    # Use client
    supabase = get_supabase_client()
    
    # Data query example
    # response = supabase.table('your_table').select('*').execute()
```

### Supabase Project Information

- **Project URL**: `https://bvowxbpqtfpkkxkzsumf.supabase.co`
- **GitHub Repository**: [https://github.com/Siyeolryu/ica-github](https://github.com/Siyeolryu/ica-github)

## Important Notes

1. **API Key Security**
   - Never commit `.env` file to Git
   - Ensure `.env` is included in `.gitignore`
   - Use Supabase service role key only on server side

2. **AI Analysis Costs**
   - AI analysis incurs costs, so only analyze non-ad reviews
   - API key issuance: https://console.anthropic.com/settings/keys

3. **Medical Information Disclaimer**
   - Analysis results are for reference only, not medical diagnosis
   - All analysis results include a disclaimer

## GitHub Repository

- **Repository**: [https://github.com/Siyeolryu/ica-github](https://github.com/Siyeolryu/ica-github)

## License

This project is developed for team project use.

## Contributors

- Logic Designer: Reliability verification engine and AI analysis logic implementation
