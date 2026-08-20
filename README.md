# 🌿 DriftShield Local

Local-first pesticide drift exposure screening dashboard using authorized spray-event records.

## Features
- Explainable 0–100 drift-screening score
- Monitor / Moderate Review / High Review / Critical Review
- Wind, weather, proximity, spray activity, and mitigation signals
- Field and sensitive-site analytics
- Local CSV validation and scored export
- Interactive Plotly dashboards
- No external APIs

This is operational screening support, not toxicological exposure modeling or health-risk assessment. Included data is synthetic.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```
