"""
Saved Plans Module - Plan Persistence and Reuse

Provides:
- Save normalization plans for future reuse
- List and retrieve saved plans
- Column compatibility validation
- Usage tracking
"""

import json
import hashlib
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

# Storage path
DATA_DIR = Path(__file__).parent / "data"
PLANS_FILE = DATA_DIR / "saved_plans.json"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SavedPlan:
    """A saved normalization plan for reuse."""
    id: str
    name: str
    created_at: str
    columns_hash: str  # Hash of column names for compatibility check
    columns: List[str]  # Original column names
    plan_json: Dict[str, Any]  # The full NormalizationPlanV13 as dict
    usage_count: int = 0
    last_used: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SavedPlan':
        return cls(**data)


# ============================================================================
# STORAGE FUNCTIONS
# ============================================================================

def _ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_plans() -> List[SavedPlan]:
    """Load all saved plans from storage."""
    _ensure_data_dir()
    
    if not PLANS_FILE.exists():
        return []
    
    try:
        with open(PLANS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [SavedPlan.from_dict(p) for p in data]
    except Exception as e:
        logger.error(f"Error loading saved plans: {e}")
        return []


def _save_plans(plans: List[SavedPlan]):
    """Save all plans to storage."""
    _ensure_data_dir()
    
    try:
        with open(PLANS_FILE, 'w', encoding='utf-8') as f:
            json.dump([p.to_dict() for p in plans], f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving plans: {e}")
        raise


# ============================================================================
# COLUMN HASHING
# ============================================================================

def compute_columns_hash(columns: List[str]) -> str:
    """
    Compute a stable hash of column names for compatibility checking.
    
    Normalizes columns (lowercase, sorted) to handle minor variations.
    """
    normalized = sorted([c.strip().lower() for c in columns])
    hash_input = "|".join(normalized)
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


# ============================================================================
# PUBLIC API
# ============================================================================

def save_plan(
    plan_dict: Dict[str, Any], 
    columns: List[str],
    name: Optional[str] = None
) -> SavedPlan:
    """
    Save a normalization plan for future reuse.
    
    Args:
        plan_dict: The NormalizationPlanV13 as a dictionary
        columns: List of CSV column names
        name: Optional human-readable name (auto-generated if not provided)
    
    Returns:
        The saved plan with generated ID
    """
    plans = _load_plans()
    
    plan_id = str(uuid.uuid4())[:8]
    columns_hash = compute_columns_hash(columns)
    
    # Auto-generate name if not provided
    if not name:
        template = plan_dict.get('template_fingerprint', {}).get('recommended_template_name', 'custom')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        name = f"{template}_{timestamp}"
    
    saved_plan = SavedPlan(
        id=plan_id,
        name=name,
        created_at=datetime.now().isoformat(),
        columns_hash=columns_hash,
        columns=columns,
        plan_json=plan_dict,
        usage_count=0
    )
    
    plans.append(saved_plan)
    _save_plans(plans)
    
    logger.info(f"Saved plan '{name}' with id {plan_id}")
    return saved_plan


def list_plans() -> List[Dict[str, Any]]:
    """
    List all saved plans with summary info.
    
    Returns:
        List of plan summaries (id, name, created_at, usage_count, columns)
    """
    plans = _load_plans()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "created_at": p.created_at,
            "usage_count": p.usage_count,
            "last_used": p.last_used,
            "columns_count": len(p.columns),
            "columns_preview": p.columns[:5] if p.columns else []
        }
        for p in plans
    ]


def get_plan(plan_id: str) -> Optional[SavedPlan]:
    """
    Retrieve a specific saved plan by ID.
    
    Returns:
        The SavedPlan or None if not found
    """
    plans = _load_plans()
    
    for p in plans:
        if p.id == plan_id:
            return p
    
    return None


def check_compatibility(
    plan_id: str, 
    csv_columns: List[str]
) -> Tuple[bool, str, List[str]]:
    """
    Check if a saved plan is compatible with a CSV's columns.
    
    Args:
        plan_id: ID of the saved plan
        csv_columns: Columns from the new CSV
    
    Returns:
        (is_compatible, message, missing_columns)
    """
    plan = get_plan(plan_id)
    
    if not plan:
        return False, f"Plan {plan_id} not found", []
    
    # Compute hash of new columns
    new_hash = compute_columns_hash(csv_columns)
    
    if new_hash == plan.columns_hash:
        return True, "Columns match exactly", []
    
    # Find specific differences
    plan_cols_normalized = {c.strip().lower() for c in plan.columns}
    new_cols_normalized = {c.strip().lower() for c in csv_columns}
    
    missing_in_csv = plan_cols_normalized - new_cols_normalized
    extra_in_csv = new_cols_normalized - plan_cols_normalized
    
    diffs = []
    if missing_in_csv:
        diffs.append(f"Missing columns: {', '.join(sorted(missing_in_csv))}")
    if extra_in_csv:
        diffs.append(f"Extra columns: {', '.join(sorted(extra_in_csv))}")
    
    return False, "; ".join(diffs), list(missing_in_csv)


def increment_usage(plan_id: str) -> bool:
    """
    Increment usage count for a plan after successful execution.
    
    Returns:
        True if successful, False if plan not found
    """
    plans = _load_plans()
    
    for p in plans:
        if p.id == plan_id:
            p.usage_count += 1
            p.last_used = datetime.now().isoformat()
            _save_plans(plans)
            logger.info(f"Plan {plan_id} usage incremented to {p.usage_count}")
            return True
    
    return False


def delete_plan(plan_id: str) -> bool:
    """
    Delete a saved plan.
    
    Returns:
        True if deleted, False if not found
    """
    plans = _load_plans()
    initial_count = len(plans)
    
    plans = [p for p in plans if p.id != plan_id]
    
    if len(plans) < initial_count:
        _save_plans(plans)
        logger.info(f"Deleted plan {plan_id}")
        return True
    
    return False
