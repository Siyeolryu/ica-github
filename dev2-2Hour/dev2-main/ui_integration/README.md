# Health Supplement Review Fact-Check System - Streamlit UI

Review analysis and comparison dashboard for 5 lutein products

## Project Structure

```
ui_integration/
├── app.py                  # [Main] Tab-based dynamic dashboard logic
├── visualizations.py       # [Chart] Plotly-based high-resolution visualization components
├── supabase_data.py        # [Data] Supabase data manager (logic_designer compliant)
├── requirements.txt        # [Env] Project dependency management
└── README.md               # [Doc] Project specification
```

## Installation

### 1. Create Virtual Environment (Recommended)

```bash
cd ui_integration
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Supabase

Create `.streamlit/secrets.toml` file:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your_anon_key_here"
ANTHROPIC_API_KEY = "your_anthropic_api_key_here"
```

## Run Application

```bash
streamlit run app.py
```

Browser will automatically open at http://localhost:8501

## Features

### 1. Product Overview (Product Cards)
- Product name, brand, price
- Reliability gauge chart
- Reliability grade badge (HIGH/MEDIUM/LOW)

### 2. Comprehensive Comparison Table
- Reliability score
- Advertising suspicion rate
- Repurchase rate
- One month usage rate
- Average rating

### 3. Visualization Analysis
- **Radar Chart**: Multi-dimensional comparison of products
- **Price Comparison Chart**: Brand-wise price visualization
- **Review Sentiment Chart**: Sentiment analysis visualization
- **Trust Score Comparison**: Side-by-side trust score comparison

### 4. AI Pharmacist Insights
Detailed analysis for each product:
- Summary
- Efficacy analysis
- Side effects information
- Usage recommendations
- Warnings
- 8-step checklist results

### 5. Review Detail View
- Product-wise review list (20 per product)
- Advertising suspicion review highlighting
- Rating filtering
- Rating distribution chart
- Verified purchase/Repurchase/1 month+ badges

## Data Structure

### Product Information
- Product ID, name, brand
- Price, category
- Rating average, rating count
- Product URL

### Review Information
- Review text, rating, date
- Repurchase status, one month usage status
- Reviewer, verified purchase status
- Various review types (positive/negative/neutral/advertising)

### Analysis Results
- Reliability score (0-100)
- Reliability grade (HIGH/MEDIUM/LOW)
- 8-step checklist results
- AI pharmacist analysis (summary, efficacy, side effects, recommendations, warnings)

## Tech Stack

- **Streamlit**: Web UI framework
- **Plotly**: Interactive charts
- **Pandas**: Data processing
- **Supabase**: Backend database
- **Anthropic Claude**: AI analysis engine

## Reliability Analysis Criteria (8-Step Checklist)

1. Verified purchase rate (70% or higher)
2. Repurchase rate (30% or higher)
3. Long-term usage rate (50% or higher)
4. Rating distribution appropriateness (30-90% high ratings)
5. Review length (average 50+ characters)
6. Time distribution naturalness
7. Advertising review detection (less than 10%)
8. Reviewer diversity (80% or higher)

## Key Features

- Real-time product search functionality
- Responsive layout (automatic horizontal/vertical layout adjustment)
- Interactive charts (zoom/pan/hover information)
- Automatic advertising review detection and highlighting
- Various filtering options
- Product comparison (main product + 2 comparison products)
- Auto-updating charts on product selection

## Architecture (logic_designer Compliant)

### Class-Based Design
- `SupabaseConfigManager`: Supabase configuration management
- `SupabaseDataManager`: Supabase data query and management
- `ChecklistGenerator`: 8-step checklist generation (integrated with logic_designer.AdChecklist)
- `AIAnalysisGenerator`: AI pharmacist analysis generation (integrated with logic_designer.PharmacistAnalyzer)

### Integration with logic_designer
- Uses `AdChecklist` for 13-step advertising detection
- Uses `PharmacistAnalyzer` for AI analysis
- Supports `ProductCheckCriteria` for product-specific criteria
- Safe error handling with fallback mechanisms

## Future Improvements

- [ ] Real-time data synchronization
- [ ] More product categories
- [ ] User login and favorites functionality
- [ ] PDF report export
- [ ] Enhanced product comparison features
- [ ] Nutrition information integration
