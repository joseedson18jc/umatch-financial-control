# UMatch Financial Control System

A comprehensive financial management system with CSV import, data normalization, P&L analysis, and AI-powered insights.

## Project Structure

```
.
├── backend/              # FastAPI Python backend
│   ├── main.py          # Main application entry point
│   ├── logic.py         # Business logic and calculations
│   ├── models.py        # Pydantic data models
│   ├── auth.py          # Authentication logic
│   ├── ai_service.py    # AI integration
│   ├── validation.py    # Data validation
│   ├── requirements.txt # Python dependencies
│   └── data/            # Data storage directory
│
├── frontend/            # React + TypeScript + Vite frontend
│   ├── src/            # Source files
│   ├── public/         # Static assets
│   ├── dist/           # Built files
│   └── package.json    # Node dependencies
│
├── docs/               # Documentation files
│   ├── DEPLOY.md
│   ├── DEPLOYMENT.md
│   ├── MANUAL_DO_USUARIO.md
│   └── QUICK_DEPLOY.md
│
└── data/              # Sample data files
    ├── Business_Plan_Umatch_Automatizado_FINAL.xlsx
    └── Extratodemovimentações-2025-ExtratoFinanceiro.csv
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip3 install -r requirements.txt
cp ../.env.example .env
# Edit .env with your configuration
python3 main.py
```

Backend will run on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

### 3. Production Build

```bash
# Build frontend
cd frontend
npm run build

# Run backend (serves frontend automatically)
cd ../backend
python3 main.py
```

## Features

- **CSV Import & Normalization**: Import financial data from various formats
- **P&L Analysis**: Profit & Loss statements with customizable categories
- **Dashboard**: Interactive financial visualizations
- **AI Insights**: OpenAI-powered financial analysis (requires API key)
- **Multi-user Support**: Authentication and user management
- **Budget Management**: Create and track budgets
- **Forecasting**: Financial projections based on historical data

## Environment Variables

See `.env.example` for required environment variables:

- `OPENAI_API_KEY`: (Optional) For AI-powered insights
- `FRONTEND_URL`: Production frontend URL for CORS
- `STORE_NET_RATE`: Store net rate for calculations (default: 0.85)
- `SECRET_KEY`: JWT secret key (change in production!)

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

Default credentials:
- Username: `admin`
- Password: `admin123`

**⚠️ Change these in production!**

## Deployment

See deployment guides:
- [Quick Deploy](QUICK_DEPLOY.md)
- [Full Deployment Guide](DEPLOYMENT.md)
- [Render.com Deployment](render.yaml)

## Scripts

- `build.sh`: Build frontend and prepare for deployment
- `run_backend.sh`: Start backend server
- `Makefile`: Common development tasks

## Documentation

- [User Manual](MANUAL_DO_USUARIO.md) (Portuguese)
- [Business Plan Documentation](DOCUMENTACAO_Business_Plan_Umatch.md)
- [Quick Start Guide](Guia%20Rápido%20de%20Uso%20-%20Business%20Plan%20Umatch%20Automatizado.md)

## Support

For issues and questions, refer to the documentation files in the project root.

## License

Proprietary - UMatch Financial Control System
