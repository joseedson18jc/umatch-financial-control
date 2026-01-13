from fastapi import FastAPI, HTTPException, Body, Depends, status, Form
from fastapi.middleware.cors import CORSMiddleware
try:
    from fastapi import UploadFile, File  # type: ignore
    from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
    _multipart_available = True
except Exception:
    UploadFile = None  # type: ignore
    File = None  # type: ignore
    OAuth2PasswordRequestForm = None  # type: ignore
    _multipart_available = False
from typing import List, Optional
import pandas as pd
from models import MappingItem, MappingUpdate, DashboardData, PnLResponse
from logic import (
    process_upload,
    get_initial_mappings,
    calculate_pnl,
    get_dashboard_data,
    calculate_forecast,
    get_unmapped_diagnostics,
    suggest_mappings,
    normalize_text_helper,
)
from ai_service import generate_insights
from auth import Token, create_access_token, get_current_user, USERS_DB, verify_password, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
"""Main FastAPI application for financial control.

This module attempts to import and load environment variables using
python-dotenv. If the optional dependency is not available, the
`load_dotenv` function is stubbed out so that the application can
still run without raising an ImportError.
"""
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    # Fallback stub if python-dotenv is not installed
    def load_dotenv(*args, **kwargs):  # type: ignore
        return False

import os
import json
import pickle
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]

# Add production frontend URL from env
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Keep * for now to avoid issues if env var is missing or mismatch
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (rest of imports)

# Authentication endpoint
@app.post("/api/login", response_model=Token)
async def login(
    username: str = Form(None),
    password: str = Form(None),
    credentials: dict = Body(None)
):
    """
    Login endpoint for admin users.
    Accepts either form data or JSON body with 'username'/'email' and 'password' fields,
    returns a JWT access token.
    """
    # Support both form data and JSON
    if credentials:
        username = credentials.get("username") or credentials.get("email")
        password = credentials.get("password")
    # If form data, username and password are already set from Form()
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password required")
    user = USERS_DB.get(username)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Data persistence configuration
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "current_data.pkl"
MAPPINGS_PATH = DATA_DIR / "mappings.json"
OVERRIDES_PATH = DATA_DIR / "overrides.json"
METADATA_PATH = DATA_DIR / "metadata.json"

# State (with persistence)
current_df = None
current_mappings = get_initial_mappings()
current_overrides = {} # Format: {"line_num": {"month": value}}

# Persistence helper functions
def save_data():
    """Save current dataframe and mappings to disk"""
    try:
        if current_df is not None:
            with open(CSV_PATH, 'wb') as f:
                pickle.dump(current_df, f)
            
        # Save mappings
        mappings_dict = [m.model_dump() for m in current_mappings]
        with open(MAPPINGS_PATH, 'w') as f:
            json.dump(mappings_dict, f)
            
        # Save overrides
        with open(OVERRIDES_PATH, 'w') as f:
            json.dump(current_overrides, f)
        
        # Save metadata
        metadata = {
            "last_upload": datetime.now().isoformat(),
            "rows": len(current_df) if current_df is not None else 0
        }
        with open(METADATA_PATH, 'w') as f:
            json.dump(metadata, f)
            
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

def load_data():
    """Load dataframe and mappings from disk on startup"""
    global current_df, current_mappings, current_overrides
    
    try:
        # Load dataframe
        if CSV_PATH.exists():
            with open(CSV_PATH, 'rb') as f:
                current_df = pickle.load(f)
            
            # Clean columns of loaded data to match new logic
            if current_df is not None:
                current_df.columns = [c.strip() for c in current_df.columns]
                logger.info(f"✅ Loaded data: {len(current_df)} rows (Columns cleaned)")
        
        # Load mappings
        if MAPPINGS_PATH.exists():
            with open(MAPPINGS_PATH, 'r') as f:
                mappings_dict = json.load(f)
                current_mappings = [MappingItem(**m) for m in mappings_dict]
            logger.info(f"✅ Loaded {len(current_mappings)} mappings")
            
        # Load overrides
        if OVERRIDES_PATH.exists():
            with open(OVERRIDES_PATH, 'r') as f:
                current_overrides = json.load(f)
            logger.info(f"✅ Loaded overrides for {len(current_overrides)} lines")
        
        # Load metadata
        if METADATA_PATH.exists():
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
            logger.info(f"✅ Last upload: {metadata.get('last_upload', 'Unknown')}")
                
    except Exception as e:
        logger.warning(f"⚠️ Error loading data: {e}")
        current_df = None
        current_mappings = get_initial_mappings()
        current_overrides = {}

@app.on_event("startup")
async def startup_event():
    """Load persisted data on startup"""
    load_data()



@app.post("/pnl/override")
def update_pnl_override(data: dict):
    """Update a specific cell in the P&L"""
    global current_overrides
    
    line_num = str(data.get("line_number"))
    month = data.get("month")
    value = data.get("value")
    
    if not line_num or not month:
        raise HTTPException(status_code=400, detail="Missing line_number or month")
        
    if line_num not in current_overrides:
        current_overrides[line_num] = {}
        
    current_overrides[line_num][month] = float(value)
    save_data()
    return {"message": "Override saved"}

@app.delete("/api/pnl/overrides")
def clear_pnl_overrides(current_user: dict = Depends(get_current_user)):
    """Clear all P&L overrides"""
    global current_overrides
    current_overrides = {}
    save_data()
    return {"message": "All overrides cleared"}

@app.get("/status")
def get_status():
    """Health check endpoint that returns data availability status"""
    has_data = current_df is not None
    metadata = {}
    
    if METADATA_PATH.exists():
        try:
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
        except:
            pass
    
    return {
        "status": "healthy",
        "data_loaded": has_data,
        "rows": len(current_df) if has_data else 0,
        "last_upload": metadata.get("last_upload"),
        "mappings_count": len(current_mappings)
    }

@app.post("/upload")
async def upload_file(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload CSV content to the server.

    Instead of relying on UploadFile and multipart/form-data (which requires
    the optional python-multipart package), this endpoint accepts a JSON
    payload with a base64-encoded CSV file in the 'file' field.

    Example JSON body:

        {
            "file": "...base64-encoded contents..."
        }
    """
    global current_df
    import base64
    file_b64 = payload.get("file")
    if not file_b64:
        raise HTTPException(status_code=400, detail="Missing 'file' in request body")
    try:
        content = base64.b64decode(file_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")
    try:
        current_df = process_upload(content)
        save_data()  # Persist to disk
        return {"message": "File processed successfully", "rows": len(current_df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/data")
def clear_data(current_user: dict = Depends(get_current_user)):
    """Clear all uploaded data"""
    global current_df
    current_df = None
    # Also clear metadata
    if CSV_PATH.exists():
        os.remove(CSV_PATH)
    if METADATA_PATH.exists():
        os.remove(METADATA_PATH)
    return {"message": "Data cleared successfully"}

@app.get("/mappings", response_model=List[MappingItem])
def get_mappings(current_user: dict = Depends(get_current_user)):
    return current_mappings

@app.post("/mappings")
def update_mappings(update: MappingUpdate, current_user: dict = Depends(get_current_user)):
    global current_mappings
    current_mappings = update.mappings
    save_data()  # Persist to disk
    return {"message": "Mappings updated"}

@app.delete("/api/mappings")
def reset_mappings(current_user: dict = Depends(get_current_user)):
    """Reset mappings to default"""
    global current_mappings
    current_mappings = get_initial_mappings()
    save_data()
    return {"message": "Mappings reset to default"}

@app.get("/pnl", response_model=PnLResponse)
def get_pnl(
    start_date: str = None, 
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
):
    global current_df, current_overrides
    
    # Lazy load if data is missing but might exist on disk
    if current_df is None:
        logger.warning("⚠️ Data missing in memory, attempting lazy load...")
        load_data()
        
    if current_df is None or current_df.empty:
        raise HTTPException(status_code=404, detail="No data loaded. Please upload a CSV file.")
    
    return calculate_pnl(current_df, current_mappings, current_overrides, start_date, end_date)

@app.get("/pnl/transactions/{line_number}")
def get_pnl_line_transactions(
    line_number: int,
    month: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all transactions that contribute to a specific P&L line.
    
    Args:
        line_number: The P&L line number (e.g., 9 for Marketing, 56 from mapping)
        month: Optional month filter in format '2024-10' or integer
    
    Returns:
        JSON with line details and list of transactions
    """
    global current_df, current_mappings
    
    if current_df is None:
        load_data()
    
    if current_df is None or current_df.empty:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    # Find mapping for this line number  
    line_mapping = None
    for mapping in current_mappings:
        try:
            if int(mapping.linha_pl) == line_number:
                line_mapping = mapping
                break
        except:
            continue
    
    if not line_mapping:
        raise HTTPException(
            status_code=404,
            detail=f"No mapping found for line {line_number}"
        )
    
    # Filter dataframe
    filtered_df = current_df.copy()
    
    # Apply month filter if provided
    if month:
        try:
            if '-' in str(month):  # Format: 'YYYY-MM'
                filtered_df = filtered_df[filtered_df['Mes_Competencia'].astype(str) == month]
            else:  # Could be Period object comparison
                filtered_df = filtered_df[filtered_df['Mes_Competencia'] == month]
        except Exception as e:
            logger.warning(f"Month filter error: {e}")
    
    # Apply Centro de Custo filter
    if line_mapping.centro_custo:
        filtered_df = filtered_df[
            filtered_df['Centro de Custo 1'].astype(str).str.contains(
                line_mapping.centro_custo, case=False, na=False, regex=False
            )
        ]
    
    # Apply Fornecedor/Cliente filter
    if line_mapping.fornecedor_cliente and line_mapping.fornecedor_cliente != "Diversos":
        filtered_df = filtered_df[
            filtered_df['Nome do fornecedor/cliente'].astype(str).str.contains(
                line_mapping.fornecedor_cliente, case=False, na=False, regex=False
            )
        ]
    
    # Build transaction list
    transactions = []
    total = 0.0
    
    for _, row in filtered_df.iterrows():
        try:
            date_val = row.get('Data de competência')
            date_str = date_val.strftime('%Y-%m-%d') if pd.notna(date_val) else ''
        except:
            date_str = ''
            
        transaction = {
            "date": date_str,
            "month": str(row.get('Mes_Competencia', '')),
            "centro_custo": str(row.get('Centro de Custo 1', '')),
            "fornecedor": str(row.get('Nome do fornecedor/cliente', '')),
            "descricao": str(row.get('Descrição', '')),
            "valor": float(row.get('Valor_Num', 0)),
            "categoria": str(row.get('Plano de contas', ''))
        }
        transactions.append(transaction)
        total += transaction['valor']
    
    return {
        "line_number": line_number,
        "description": line_mapping.descricao,
        "centro_custo_filter": line_mapping.centro_custo,
        "fornecedor_filter": line_mapping.fornecedor_cliente,
        "month": month if month else "all",
        "total": round(total, 2),
        "count": len(transactions),
        "transactions": transactions
    }

@app.get("/validate")
def validate_data(current_user: dict = Depends(get_current_user)):
    """
    Validate calculation consistency between Dashboard and P&L.
    Returns validation results and any errors found.
    """
    from validation import validate_dashboard_pnl_consistency, validate_calculation_logic
    
    global current_df, current_mappings, current_overrides
    
    if current_df is None:
        load_data()
    
    if current_df is None or current_df.empty:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    # Calculate P&L and Dashboard
    pnl_data = calculate_pnl(current_df, current_mappings, current_overrides)
    dashboard_data = get_dashboard()
    
    # Run validations
    dashboard_valid, dashboard_errors = validate_dashboard_pnl_consistency(
        dashboard_data, pnl_data
    )
    
    latest_month = pnl_data['headers'][-1] if pnl_data['headers'] else None
    calc_valid = True
    calc_errors = []
    
    if latest_month:
        calc_valid, calc_errors = validate_calculation_logic(pnl_data, latest_month)
    
    return {
        "valid": dashboard_valid and calc_valid,
        "dashboard_validation": {
            "valid": dashboard_valid,
            "errors": dashboard_errors
        },
        "calculation_validation": {
            "valid": calc_valid,
            "errors": calc_errors,
            "month_validated": latest_month
        }
    }

@app.post("/api/insights")
def get_ai_insights(request: dict, current_user: dict = Depends(get_current_user)):
    """
    Generate AI insights from financial data using OpenAI.
    """
    try:
        data = request.get("data", {})
        api_key = request.get("api_key")
        
        if not data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        insights = generate_insights(data, api_key)
        return {"insights": insights}
    except Exception as e:
        logger.error(f"Error in /api/insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_model=DashboardData)
def get_dashboard(current_user: dict = Depends(get_current_user)):
    global current_df, current_mappings, current_overrides
    
    # Lazy load if data is missing but might exist on disk
    if current_df is None:
        print("⚠️ Data missing in memory, attempting lazy load...")
        load_data()
        
    if current_df is None:
        # Return empty structure
        return DashboardData(kpis={}, monthly_data=[], cost_structure={})
    
    # Note: get_dashboard_data needs to be updated to accept overrides too if we want charts to reflect edits
    # For now, let's update logic.py signature for get_dashboard_data as well
    return get_dashboard_data(current_df, current_mappings, current_overrides)

@app.get("/api/forecast")
def get_forecast(months: int = 3, current_user: dict = Depends(get_current_user)):
    """
    Get financial forecast for the next N months.
    """
    global current_df, current_mappings, current_overrides
    
    if current_df is None:
        load_data()
        
    return calculate_forecast(current_df, current_mappings, current_overrides, months_ahead=months)

# ---------------------------------------------------------------------------
# Unmapped diagnostics and mapping suggestions
# ---------------------------------------------------------------------------

@app.get("/api/unmapped")
def get_unmapped(month: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Return diagnostics for unmapped transactions.

    Args:
        month: Optional month filter (YYYY-MM). If provided, only that month's transactions are considered.

    Returns:
        A dictionary with counts, amounts and breakdowns of unmapped transactions.
    """
    global current_df, current_mappings
    if current_df is None:
        load_data()
    if current_df is None or current_df.empty:
        raise HTTPException(status_code=404, detail="No data loaded")
    return get_unmapped_diagnostics(current_df, current_mappings, month)


@app.post("/api/mappings/suggest")
def get_mapping_suggestions(current_user: dict = Depends(get_current_user)):
    """Generate mapping suggestions for unmapped supplier/cost center combos.

    Returns a list of MappingItem dictionaries that the user can review and apply.
    """
    global current_df, current_mappings
    if current_df is None:
        load_data()
    if current_df is None or current_df.empty:
        raise HTTPException(status_code=404, detail="No data loaded")
    suggestions = suggest_mappings(current_df, current_mappings)
    # Return list of dicts for JSON serialization
    return {"suggestions": [s.model_dump() for s in suggestions]}


@app.post("/api/mappings/apply")
def apply_mapping_suggestions(suggestions: List[MappingItem] = Body(...), current_user: dict = Depends(get_current_user)):
    """Apply mapping suggestions to the current mapping list.

    Accepts a list of MappingItem objects. Any new mapping not already present
    (based on centro_custo and fornecedor_cliente) will be appended.
    """
    global current_mappings
    # Normalize existing pairs for duplicate check
    existing_pairs = set()
    for m in current_mappings:
        existing_pairs.add((normalize_text_helper(m.centro_custo), normalize_text_helper(m.fornecedor_cliente)))
    added = 0
    for m in suggestions:
        # m might be Pydantic model or dict; convert to MappingItem
        if isinstance(m, dict):
            try:
                m_obj = MappingItem(**m)
            except Exception as e:
                continue
        else:
            m_obj = m
        key = (normalize_text_helper(m_obj.centro_custo), normalize_text_helper(m_obj.fornecedor_cliente))
        if key not in existing_pairs:
            current_mappings.append(m_obj)
            existing_pairs.add(key)
            added += 1
    if added:
        save_data()
    return {"added": added, "total_mappings": len(current_mappings)}

# ---------------------------------------------------------------------------
# AI Table Parser Endpoints (Anthropic Claude)
# ---------------------------------------------------------------------------

@app.post("/api/ai/analyze-csv")
async def analyze_csv_with_ai(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze CSV structure using AI to detect column mappings.
    
    Request body:
        {
            "csv_sample": "First 20-50 rows of CSV as string",
            "api_key": "Anthropic API key (optional, uses env var if not provided)"
        }
    """
    from ai_table_parser import analyze_csv_structure
    
    csv_sample = payload.get("csv_sample", "")
    api_key = payload.get("api_key")
    
    if not csv_sample:
        raise HTTPException(status_code=400, detail="csv_sample is required")
    
    result = analyze_csv_structure(csv_sample, api_key)
    return result


@app.post("/api/ai/suggest-mappings")
async def ai_suggest_mappings(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-powered mapping suggestions for unmapped transactions.
    
    Request body:
        {
            "api_key": "Anthropic API key (optional)"
        }
    """
    from ai_table_parser import suggest_category_mappings
    
    global current_df, current_mappings
    
    if current_df is None:
        load_data()
    
    if current_df is None or current_df.empty:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    api_key = payload.get("api_key")
    
    # Get unmapped transactions sample
    from logic import get_unmapped_diagnostics
    diagnostics = get_unmapped_diagnostics(current_df, current_mappings)
    
    # Build transaction samples from unmapped data
    unmapped_sample = []
    for item in diagnostics.get("by_supplier", [])[:20]:
        unmapped_sample.append({
            "fornecedor": item.get("name", ""),
            "valor": item.get("amount", 0)
        })
    
    # Get existing mappings as dicts
    existing = [m.model_dump() for m in current_mappings]
    
    suggestions = suggest_category_mappings(unmapped_sample, existing, api_key)
    
    return {"suggestions": suggestions, "unmapped_count": diagnostics.get("total_unmapped_count", 0)}


@app.post("/api/ai/smart-upload")
async def smart_upload_with_ai(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload CSV with AI-assisted format detection and column mapping.
    
    Request body:
        {
            "file": "base64-encoded CSV content",
            "api_key": "Anthropic API key (optional)"
        }
    """
    global current_df
    import base64
    from ai_table_parser import detect_csv_format, analyze_csv_structure
    
    file_b64 = payload.get("file")
    api_key = payload.get("api_key")
    
    if not file_b64:
        raise HTTPException(status_code=400, detail="Missing 'file' in request body")
    
    try:
        content = base64.b64decode(file_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")
    
    # Use AI to detect format
    encoding, separator, date_format = detect_csv_format(content, api_key)
    
    # Get sample for analysis
    try:
        sample = content.decode(encoding)[:3000]
    except:
        sample = content.decode('latin-1', errors='ignore')[:3000]
    
    # Analyze structure
    analysis = {}
    if api_key:
        analysis = analyze_csv_structure(sample, api_key)
    
    # Process with standard upload
    try:
        current_df = process_upload(content)
        save_data()
        
        return {
            "message": "File processed successfully with AI assistance",
            "rows": len(current_df),
            "detected_format": analysis.get("detected_format", "Unknown"),
            "column_mappings": analysis.get("column_mappings", {}),
            "suggestions": analysis.get("suggestions", []),
            "encoding": encoding,
            "separator": separator
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Serve the built frontend (Vite) from the dist folder
from fastapi.responses import FileResponse, HTMLResponse

# Resolve the absolute path to the frontend build output
# In Docker: /app/frontend/dist, Local: ../frontend/dist
frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend", "dist"))
if not os.path.exists(frontend_dist_path):
    # Fallback for local development
    frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

logger.info(f"🔍 Looking for frontend build at: {frontend_dist_path}")
logger.info(f"📁 Frontend build exists: {os.path.exists(frontend_dist_path)}")
if os.path.exists(frontend_dist_path):
    logger.info(f"📄 Frontend build contents: {os.listdir(frontend_dist_path)}")

@app.get("/api/health")
def health_check():
    """API health check endpoint"""
    return {
        "status": "ok",
        "message": "Umatch BP Dashboard API",
        "frontend_path": frontend_dist_path,
        "frontend_exists": os.path.exists(frontend_dist_path),
        "users": list(USERS_DB.keys())  # Show available usernames for debugging
    }

# IMPORTANT: This must be the LAST route defined - it's a catch-all
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve SPA frontend or API 404"""
    
    # Handle empty path (root)
    if full_path == "":
        full_path = "index.html"
    
    # Check if frontend dist exists at all
    if not os.path.exists(frontend_dist_path):
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>Build Missing</title></head>
            <body style="font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
                <h1>❌ Frontend Build Not Found</h1>
                <p>The frontend build directory is missing. This usually means the build command failed or hasn't run yet.</p>
                <h2>Expected path:</h2>
                <code style="background: #f5f5f5; padding: 10px; display: block;">{frontend_dist_path}</code>
                <h2>To fix this on Render:</h2>
                <ol>
                    <li>Go to your Render dashboard</li>
                    <li>Update the <strong>Build Command</strong> to:<br>
                        <code style="background: #f5f5f5; padding: 10px; display: block; margin: 10px 0;">
                        cd frontend && npm ci && npm run build && cd .. && pip install -r backend/requirements.txt
                        </code>
                    </li>
                    <li>Click "Manual Deploy" → "Clear build cache & deploy"</li>
                </ol>
                <hr>
                <p><a href="/api/health">Check API Health</a></p>
            </body>
            </html>
            """,
            status_code=503
        )
    
    # Try to serve the requested file
    file_path = os.path.join(frontend_dist_path, full_path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # If not found, serve index.html for SPA routing
    index_path = os.path.join(frontend_dist_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Complete failure
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Build Incomplete</title></head>
        <body style="font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>⚠️ Frontend Build Incomplete</h1>
            <p>The build directory exists but index.html is missing.</p>
            <p>Build path: <code>{frontend_dist_path}</code></p>
            <p>Files found: <code>{os.listdir(frontend_dist_path) if os.path.exists(frontend_dist_path) else 'N/A'}</code></p>
        </body>
        </html>
        """,
        status_code=500
    )

