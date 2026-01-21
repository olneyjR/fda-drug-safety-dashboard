# FDA Drug Safety Dashboard

Real-time adverse drug event monitoring dashboard powered by the FDA FAERS API.

## Overview

This dashboard provides comprehensive analysis of adverse drug events reported to the FDA. It fetches live data directly from the OpenFDA API, processes and transforms the data in real-time, and presents interactive visualizations for drug safety monitoring.

**Live Demo:** [View Dashboard](https://olneyjr-fda-drug-safety-dashboard.streamlit.app)

## Features

- **Live FDA API Integration** - Direct connection to OpenFDA adverse events API
- **Real-time Data Processing** - Fetches and transforms 5,000+ recent adverse event records
- **Risk Classification** - Automated drug risk scoring based on fatality rates and severity
- **Interactive Visualizations** - Plotly-powered charts and graphs
- **Drug Search** - Search and analyze specific medications
- **Smart Caching** - One-hour cache to optimize performance and API usage

## Dashboard Views

### Overview
Key metrics including total drugs monitored, adverse events, serious events, hospitalizations, life-threatening events, deaths, and average patient age. Includes risk distribution and demographic analysis.

### High Risk Drugs
Analysis of drugs with highest fatality rates (minimum 10 events), ranked by percentage of fatal outcomes.

### Top Drugs
Top 20 drugs by adverse event volume with scatter plot visualization showing relationship between event volume, serious event rate, and deaths.

### Demographics
Patient demographic breakdown including distribution by sex and age groups (Pediatric, Young Adult, Middle Age, Senior).

### Drug Search
Search functionality for specific medications with detailed safety metrics, event counts, and risk classification.

## Technical Architecture

### Data Pipeline

```
FDA OpenFDA API
    |
    v
API Client (rate limiting, error handling)
    |
    v
Data Extraction (5,000 records)
    |
    v
Data Transformation (age normalization, risk scoring)
    |
    v
In-Memory Analytics (Pandas DataFrames)
    |
    v
Streamlit Dashboard (cached for 1 hour)
```

### Key Transformations

**Age Normalization**
- Converts FDA age unit codes to standardized years
- Handles: Decades, Years, Months, Weeks, Days, Hours
- Bug fix: Corrects FDA code 801 (Year, previously misinterpreted as Month)

**Risk Classification Algorithm**
```python
if total_events < 5:
    return 'Minimal Data'
elif fatality_rate > 15:
    return 'High Risk'
elif fatality_rate > 5:
    return 'Moderate Risk'
else:
    return 'Low Risk'
```

**Severity Scoring (0-5 scale)**
```python
severity = (
    (serious_rate / 20) +
    (fatality_rate / 20) +
    (life_threatening / total_events * 5)
).clip(0, 5)
```

## Technology Stack

- **Frontend:** Streamlit 1.29.0
- **Data Processing:** Pandas 2.1.4
- **Visualizations:** Plotly 5.18.0
- **API Integration:** Requests 2.31.0
- **Language:** Python 3.11+

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Local Setup

```bash
# Clone repository
git clone https://github.com/olneyjR/fda-drug-safety-dashboard.git
cd fda-drug-safety-dashboard

# Install dependencies
pip install -r requirements_live.txt

# Run application
streamlit run streamlit_app_live.py
```

The application will open at `http://localhost:8501`

**Note:** First load takes 2-3 minutes to fetch data from FDA API. Subsequent loads are instant (cached).

## Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Visit https://share.streamlit.io
3. Click "New app"
4. Select repository: `olneyjR/fda-drug-safety-dashboard`
5. Set main file: `streamlit_app_live.py`
6. Click "Deploy"

### Other Platforms

**Heroku**
```bash
# Create Procfile
echo "web: streamlit run streamlit_app_live.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create fda-drug-safety
git push heroku main
```

**Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_live.txt .
RUN pip install -r requirements_live.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app_live.py"]
```

## API Rate Limiting

The FDA API has the following limits:
- 240 requests per minute (anonymous)
- 1,000 requests per minute (with API key)

This application implements automatic rate limiting with exponential backoff to stay within limits. Fetching 5,000 records typically requires ~50 API calls over 2-3 minutes.

## Performance

| Metric | Value |
|--------|-------|
| First Load | 2-3 minutes |
| Cached Load | <1 second |
| Cache Duration | 1 hour |
| Records Fetched | 5,000 |
| API Calls | ~50 |

## Data Quality

The dashboard implements several data quality measures:
- Age unit validation and conversion
- Type casting with error handling
- NULL value management
- Duplicate detection
- Outlier flagging for age (0-120 years)

## Project Structure

```
fda-drug-safety-dashboard/
├── streamlit_app_live.py      # Main dashboard application
├── utils/
│   ├── __init__.py
│   └── fda_api.py             # FDA API client and transformations
├── requirements_live.txt       # Python dependencies
└── README.md                   # This file
```

## Contributing

This is a portfolio project and not currently accepting contributions. However, feel free to fork and adapt for your own use.

## Data Source

This application uses the FDA Adverse Event Reporting System (FAERS) database accessed through the OpenFDA API.

**API Documentation:** https://open.fda.gov/apis/drug/event/

**Important:** This dashboard is for informational and educational purposes only. It should not be used for clinical decision-making or medical advice.

## License

MIT License - See LICENSE file for details

## Author

Jeffrey Olney  
Data Engineer | Healthcare Analytics

**Connect:**
- LinkedIn: [linkedin.com/in/jeffrey-olney](https://linkedin.com/in/jeffrey-olney)
- GitHub: [@olneyjR](https://github.com/olneyjR)

## Acknowledgments

- FDA OpenFDA API for providing public access to adverse event data
- Streamlit for the excellent dashboard framework
- Plotly for interactive visualization capabilities

---

**Disclaimer:** This dashboard displays adverse event reports submitted to FDA. These reports have not been scientifically or otherwise verified as to a cause and effect relationship and cannot be used to estimate incidence or calculate rates. The existence of an adverse event report does not establish causation.
