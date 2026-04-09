# PureCheck Architecture

## 1) System Architecture Diagram (Text)

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                                Frontend                                │
│  React + Vite                                                          │
│  - Home / Results / HeatMap / Dashboard / Report                      │
│  - REST calls via axios                                                │
│  - WebSocket live alerts                                               │
└───────────────────────────────┬─────────────────────────────────────────┘
																│
																│ HTTP (REST) + WS
																│
┌───────────────────────────────▼─────────────────────────────────────────┐
│                                Backend                                 │
│  Django + DRF + Channels                                               │
│  - REST API endpoints (/api/*)                                         │
│  - WebSocket consumer (/ws/alerts/<city>/)                            │
│  - Pipeline scheduler trigger (management command + APScheduler)       │
└───────────────┬───────────────────────────────┬─────────────────────────┘
								│                               │
								│ ORM                           │ Background pipeline
								│                               │
┌───────────────▼───────────────────────────────▼─────────────────────────┐
│                               PostgreSQL                                 │
│  Tables: Complaint, RiskScore, LiveAlert (+ optional extended models)    │
└───────────────┬───────────────────────────────┬─────────────────────────┘
								│                               │
								│ Reads/Writes                   │ Export
								│                               │
┌───────────────▼──────────────┐     ┌──────────▼─────────────────────────┐
│ Agent Pipeline               │     │ Power BI Data Export               │
│ - Scraper                    │     │ - purecheck_live.csv               │
│ - NLP extractor              │     │ - purecheck_complaints.csv         │
│ - Risk scorer (ML+fallback)  │     │ (generated post pipeline run)      │
└──────────────────────────────┘     └────────────────────────────────────┘
```

## 2) Pipeline Flow Diagram

```text
[Trigger]
	└─ python manage.py run_pipeline --once
		 OR scheduled run (APScheduler)

[Step 1: Scrape]
	├─ News API fetch per city (if key available)
	└─ Structured FSSAI mock feed (deterministic fallback)

[Step 2: NLP Extraction]
	├─ NER pipeline for city extraction (when available)
	├─ Zero-shot classification for food/adulterant (when available)
	└─ Keyword fallback for city/food/adulterant/severity

[Step 3: Complaint Upsert Logic]
	└─ Create Complaint records with dedupe window

[Step 4: Risk Scoring]
	├─ Extract numeric features from recent complaints
	├─ If model+scaler available:
	│    ml_score = model.predict(features)
	│    rule_score = weighted_formula(features)
	│    final_score = 0.7*ml_score + 0.3*rule_score
	└─ Else:
			 final_score = rule_score

[Step 5: Explainability]
	├─ If SHAP explainer available -> SHAP feature impacts
	└─ Else -> structured fallback explanation

[Step 6: Persist + Alert]
	├─ Update/create RiskScore(monthly key)
	├─ Create LiveAlert for MEDIUM/HIGH risk thresholds
	└─ Push alert via channel layer to websocket group

[Step 7: Export]
	└─ Auto-generate Power BI CSV files
```

## 3) API Flow Explanation

### Core API

- `GET /api/risk/?city=<city>`
	- Reads top risk vectors from `RiskScore` for current month.

- `GET /api/risk/explain/?city=<city>&food=<food>`
	- Returns `risk_score`, `confidence`, and explanation factors.
	- Uses SHAP data if present; otherwise structured fallback factors.

- `GET /api/alerts/?city=<city>`
	- Returns latest `LiveAlert` records including `risk_score`.

- `POST /api/report/`
	- Creates `Complaint(source=CITIZEN)`.
	- Validates required fields and severity range (1-5).

- `GET /api/heatmap/`
	- Returns city points (lat/lng) + highest risk score city summary.

- `GET /api/stats/`
	- Returns aggregate complaint/risk metrics for dashboard cards/charts.

- `GET /api/export/`
	- Triggers CSV export and streams downloadable risk CSV.

### WebSocket

- `ws://<host>/ws/alerts/<city>/`
	- Supports word, space, and hyphen city names.
	- Sends latest alerts on connect and push updates from pipeline.
