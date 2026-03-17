# PureCheck — Real-Time Food Adulteration Risk Intelligence System

A production-quality web application that provides real-time food adulteration risk intelligence for Indian markets. Users can search by city to get the top 5 high-risk food items with risk scores, likely adulterants, and live alerts.

## Features

- **Real-Time Risk Scoring**: ML-powered XGBoost model predicts food adulteration risk (0-100 scale)
- **Live Alert Feed**: WebSocket-powered real-time alerts as new complaints are processed
- **Multi-Source Intelligence**: Aggregates data from FSSAI, news articles, and citizen reports
- **NLP Extraction**: BERT-based entity extraction from unstructured text
- **Automated Pipeline**: APScheduler runs data collection and scoring every 6 hours
- **City-Based Search**: Search any Indian city for localized risk intelligence

## Tech Stack

**Frontend:**
- React 18 + Vite
- Tailwind CSS
- WebSocket for live updates

**Backend:**
- Django 4.2 + Django REST Framework
- Django Channels (WebSocket)
- PostgreSQL 15

**AI/ML:**
- LangChain for agent workflows
- XGBoost for risk prediction
- BERT for NLP extraction
- APScheduler for automation

## Project Structure

```
purecheck/
├── backend/          # Django application
├── frontend/         # React + Vite app
├── powerbi/          # Analytics dashboards
└── README.md
```

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Access at `http://localhost:5173`

## Database Models

- **Complaint**: Raw food adulteration complaints from FSSAI, news, or citizens
- **RiskScore**: Calculated risk score per city + food item per month
- **LiveAlert**: Real-time alerts pushed to frontend via WebSocket

## API Endpoints

- `GET /api/risk/?city=Trichy` - Top 5 risk items
- `GET /api/alerts/?city=Trichy` - Recent alerts
- `POST /api/report/` - Submit citizen complaint
- `GET /api/cities/` - Available cities
- `ws://localhost:8000/ws/alerts/<city>/` - WebSocket feed

## Production Deployment

- Use Gunicorn + Daphne for app server
- Configure PostgreSQL with proper backups
- Set up nginx reverse proxy
- Enable HTTPS/SSL
- Configure environment variables on server

## License

BTech Final Year Project
