# PureCheck Power BI Dashboard

Analytics and reporting dashboards for PureCheck.

## Files

- **purecheck_live.csv** — Risk score data (auto-generated)
- **purecheck_complaints.csv** — Complaint data (auto-generated)
- **purecheck_dashboard.pbix** — Power BI dashboard file (optional)

## How to Refresh Data

### Automatic (via API)
```bash
curl http://localhost:8000/api/export/
```

### Manual (via Django shell)
```bash
python manage.py shell
from agent.scheduler import export_to_csv
export_to_csv()
```

Then click **Refresh** in Power BI Desktop.

## Dashboards

- Risk Trends by City
- High-Risk Foods by State
- Adulterant Distribution
- Complaint Source Analysis
- Time Series Risk Evolution

## Usage

1. CSV files are auto-generated in this folder
2. Open `.pbix` files in Power BI Desktop
3. Click "Get Data" → "Text/CSV" and load the CSV files
4. Dashboard updates automatically when CSVs refresh
