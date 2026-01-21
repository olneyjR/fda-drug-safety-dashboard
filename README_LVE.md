# FDA Drug Safety Dashboard - Live API Version

Real-time adverse drug event monitoring dashboard powered by the FDA FAERS API.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements_live.txt

# Run the app
streamlit run streamlit_app_live.py
```

### Deployment (Streamlit Cloud, Heroku, etc.)

1. **Upload these files:**
   - `streamlit_app_live.py` (main app)
   - `utils/fda_api.py` (API client)
   - `requirements_live.txt` (dependencies)

2. **Set app entry point:**
   - Main file: `streamlit_app_live.py`

3. **Deploy!** No environment variables or API keys needed.

## 📊 Features

- **Live FDA API Integration** - No database required
- **Real-time Data** - Fetches 5,000 recent adverse events
- **Smart Caching** - 1-hour cache to avoid rate limits
- **Full Analytics** - Risk classification, demographics, drug search
- **Beautiful UI** - Modern design with Plotly visualizations
- **Zero Configuration** - No API keys or setup needed

## 🏗️ Architecture

```
streamlit_app_live.py
├── FDA API Client (utils/fda_api.py)
│   ├── fetch_adverse_events() → Raw JSON
│   ├── flatten_events() → Pandas DataFrame
│   └── transform_to_analytics() → Analytics-ready data
│
└── Streamlit Dashboard
    ├── Overview metrics
    ├── High risk drugs
    ├── Top drugs by volume
    ├── Demographics analysis
    └── Drug search
```

## 🔧 Technical Details

**Data Pipeline:**
1. Fetch 5,000 records from FDA API (takes ~2 minutes)
2. Flatten nested JSON structure
3. Apply Silver layer transformations (age normalization, type casting)
4. Build Gold layer aggregations (drug risk profiles)
5. Cache for 1 hour via Streamlit's `@st.cache_data`

**Key Transformations:**
- Age unit normalization (801=Year bug fix)
- Sex code mapping (1=Male, 2=Female)
- Risk classification algorithm
- Severity scoring (0-5 scale)

## 📦 Dependencies

- `streamlit==1.29.0` - Dashboard framework
- `pandas==2.1.4` - Data manipulation
- `plotly==5.18.0` - Interactive visualizations
- `requests==2.31.0` - HTTP API calls

## 🎯 Deployment Targets

**✅ Streamlit Cloud** (Recommended)
- Free tier works perfectly
- One-click deployment from GitHub
- Automatic updates on git push

**✅ Heroku**
- Add `Procfile`: `web: streamlit run streamlit_app_live.py --server.port=$PORT`
- Free tier sufficient

**✅ AWS/GCP/Azure**
- Deploy as container or VM
- Expose port 8501

## 🚨 Rate Limits

FDA API allows 240 requests/minute (anonymous). The app:
- Fetches 5,000 records per load (~50 requests)
- Caches for 1 hour
- Implements rate limiting with exponential backoff

**Normal usage:** Well within limits  
**Heavy testing:** Use the "Refresh Data" button sparingly

## 🔄 Comparing to Full Pipeline Version

| Feature | Live API | Full Pipeline |
|---------|----------|---------------|
| Setup | Zero config | Docker + Airflow + dbt |
| Deployment | Any platform | Requires containers |
| Data freshness | Every hour | Scheduled DAGs |
| Data volume | 5,000 records | Unlimited |
| Performance | ~2 min initial load | Sub-second (pre-computed) |
| Best for | Demos, prototypes | Production, scale |

## 📝 Notes

- First load takes 2-3 minutes to fetch from FDA API
- Subsequent loads are instant (cached)
- Refresh button clears cache and fetches new data
- All styling and functionality preserved from original app

## 🎨 Portfolio Value

This live API version demonstrates:
- **API Integration** - Direct REST API consumption
- **Data Engineering** - ETL logic without infrastructure
- **Smart Caching** - Performance optimization
- **Clean Architecture** - Separation of concerns
- **Production Ready** - Error handling, rate limiting

Perfect for showcasing data engineering skills without requiring reviewers to run Docker/Airflow!

## 📧 Contact

Jeffrey Olney  
[LinkedIn](https://linkedin.com/in/jeffrey-olney) | [GitHub](https://github.com/jeffrey-olney)

---

**Not for clinical use.** Educational/portfolio project only.