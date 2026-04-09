# PureCheck

PureCheck is a city-level food adulteration risk intelligence platform built with Django, Channels, React, and ML support.

It ingests complaint-like records, computes risk scores, raises live alerts, and renders these outputs in a dashboard, heatmap, and city results page.

---

## 1) What This Project Does

For each supported city, PureCheck provides:

- Top risk vectors by food item
- Risk score and confidence metadata
- Adulterant context
- Live alerts stream
- Heatmap-ready city risk points
- Dashboard analytics and export files

Typical user flow:

1. User searches for a city.
2. Frontend calls backend risk and alerts endpoints.
3. Backend returns city-specific risk vectors.
4. Frontend renders scores, trends, and live feed.

---

## 2) Current Runtime Design

### Backend

- Framework: Django 4.2 + Django REST Framework
- Realtime transport: Django Channels + Daphne
- Database: SQLite (single local database file)
- Scheduler trigger: safe background thread started only when running `runserver`

### Frontend

- React + Vite
- Axios-based API client
- WebSocket client for live alerts

### ML / Scoring

- Hybrid design support exists in codebase (ML + rule pipeline components)
- Current scheduler pipeline includes robust simulated multi-city data generation for reliable demos and evaluation

---

## 3) Architecture Overview

1. Data generation / ingestion
	 - Pipeline creates or updates complaints for supported cities.

2. Scoring
	 - Risk scores are generated per city and food item for current month.

3. Alerts
	 - Live alerts are created for higher-risk entries.

4. API layer
	 - REST endpoints provide risks, alerts, stats, heatmap, metrics, and evaluation.

5. Frontend rendering
	 - Results page for city vectors
	 - Heatmap page for geographic overview
	 - Dashboard page for aggregate analytics

---

## 4) Dynamic Multi-City Pipeline

The pipeline currently supports dynamic generation across a central city list and food/adulterant map.

Configured cities include:

- chennai
- coimbatore
- bangalore
- mumbai
- delhi
- hyderabad
- kolkata
- pune
- madurai
- trichy

Data behavior:

- Creates 2 to 3 complaint patterns per city from common food/adulterant combinations
- Severity varies in range 2 to 5
- Risk score varies in range 40 to 90
- Alerts are created for risk score greater than 60
- Duplicate-safe monthly behavior prevents runaway duplication

This provides meaningful dashboard and heatmap visuals even in fresh local environments.

---

## 5) Core Data Models

- Complaint
	- Source records (city, food item, adulterant, severity, metadata)

- RiskScore
	- Monthly city-food risk vector with risk score, confidence, explanation payload

- LiveAlert
	- Realtime alert entries shown in feed and available by API

Additional entities exist for reporting/auditing and project extensibility.

---

## 6) API Endpoints

Base URL: `http://localhost:8000`

- `GET /api/risk/?city=<city>`
	- Returns top risk vectors for requested city
	- City input is normalized (case-insensitive support)

- `GET /api/alerts/?city=<city>`
	- Returns recent alerts for a city

- `GET /api/heatmap/`
	- Returns city coordinates with risk points

- `GET /api/stats/`
	- Returns dashboard summary metrics

- `GET /api/ml-status/`
	- Runtime ML status payload

- `POST /api/run-pipeline/`
	- Triggers one pipeline run immediately

- `GET /api/system-metrics/`
	- Pipeline and API timing metrics

- `GET /api/evaluation-report/`
	- Evaluation and ablation-style report data

- `GET /api/cities/`
	- Available cities in data

- `POST /api/report/`
	- Submit user complaint

- `GET /api/export/`
	- Export CSV for reporting

WebSocket:

- `ws://localhost:8000/ws/alerts/<city>/`

---

## 7) Setup and Run

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8000`

---

## 8) Scheduler and Safety Notes

- Scheduler logic is function-based and import-safe.
- No blocking loop is executed at module import time.
- Scheduler starts from app startup path only when server process is `runserver`.
- Management commands like `migrate` and `shell` are not forced into scheduler startup.

---

## 9) Data Freshness and Reliability

The project is designed to avoid blank UI states in local/demo environments:

- Pipeline ensures broad city coverage.
- Risk and alert tables are generated with varied realistic ranges.
- API returns clear no-data messaging when applicable.

---

## 10) Known Local Warnings

You may see:

- `Redis unavailable ... Falling back to InMemoryChannelLayer.`

Meaning:

- App still works locally.
- Realtime is limited to single-process in-memory channel layer when Redis is not running.

To enable Redis-backed channels, start Redis locally on `127.0.0.1:6379`.

---

## 11) Project Structure

```text
purecheck/
	backend/
		agent/            # pipeline, NLP, scraper, scorer
		core/             # models, views, API routes, websocket consumer
		config/           # settings, ASGI/WSGI, root URLs
		ml/               # training and model assets
	frontend/
		src/
			pages/          # Home, Results, Heatmap, Dashboard, Report
			components/     # map, live feed, cards, navbar
			api/            # axios API client
	powerbi/            # generated export CSV files
```

---

## 12) Quick Health Checks

Run these from `backend`:

```bash
python manage.py run_pipeline --once
python manage.py shell -c "from core.models import Complaint,RiskScore,LiveAlert; print(Complaint.objects.count(), RiskScore.objects.count(), LiveAlert.objects.count())"
```

Expected:

- Complaint count greater than 0
- RiskScore count greater than 0
- LiveAlert count greater than 0

---

## 13) Academic Demo Checklist

Before presenting:

1. Start backend and frontend.
2. Run one pipeline cycle.
3. Open Heatmap and Dashboard pages.
4. Query city results for 3 to 4 different cities.
5. Show alerts panel and exported CSV.

This flow demonstrates end-to-end ingestion, scoring, API delivery, and UI visualization.

---

## 14) License

Academic project repository.
