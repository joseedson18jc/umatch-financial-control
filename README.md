# UMatch Financial Control

A smart financial control system powered by AI for analyzing Conta Azul exports.

## Features

- 📊 Executive Dashboard with KPIs
- 🔍 Anomaly Detection
- 📈 Trend Analysis & Forecasting
- 📋 DRE (Income Statement)
- 🛡️ Data Quality Analysis
- 🤖 AI-powered CSV Import

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/umatch-financial)

## Quick Start

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET` | Yes | Secret key for JWT tokens |
| `OPENAI_API_KEY` | No | For AI insights |
| `ANTHROPIC_API_KEY` | No | For AI CSV analysis |

## Tech Stack

- **Backend**: Python, FastAPI, Pandas, Scikit-learn
- **Frontend**: React, TypeScript, Tailwind CSS, Recharts
- **Deployment**: Docker, Render.com

## License

MIT
