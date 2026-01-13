"""
Security Utilities Module

Provides:
- Data sanitization for free-text fields
- Export safety (neutralizes Excel formula injection)
- Input validation helpers
"""

import re
import unicodedata
import logging
from typing import Optional, List, Any

logger = logging.getLogger(__name__)


# ============================================================================
# TEXT SANITIZATION
# ============================================================================

# Characters that should not appear in user input
FORBIDDEN_CHARS = [
    '\x00',     # Null byte
    '\x1b',     # Escape
    '\x7f',     # Delete
]

# Max field lengths
MAX_DESCRIPTION_LENGTH = 500
MAX_CATEGORY_LENGTH = 100
MAX_SUPPLIER_LENGTH = 200


def sanitize_text(value: str, max_length: int = 500, allow_newlines: bool = False) -> str:
    """
    Sanitize text input for safe storage and display.
    
    - Removes null bytes and control characters
    - Trims whitespace
    - Collapses multiple spaces
    - Enforces max length
    """
    if not value:
        return ""
    
    # Convert to string if needed
    value = str(value)
    
    # Remove forbidden characters
    for char in FORBIDDEN_CHARS:
        value = value.replace(char, '')
    
    # Remove control characters (except newlines if allowed)
    if allow_newlines:
        value = ''.join(c for c in value if c == '\n' or not unicodedata.category(c).startswith('C'))
    else:
        value = ''.join(c for c in value if not unicodedata.category(c).startswith('C'))
    
    # Trim and collapse whitespace
    value = value.strip()
    value = re.sub(r'\s+', ' ', value)
    
    # Enforce max length
    if len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"Text truncated to {max_length} characters")
    
    return value


def sanitize_description(value: str) -> str:
    """Sanitize description field."""
    return sanitize_text(value, MAX_DESCRIPTION_LENGTH)


def sanitize_category(value: str) -> str:
    """Sanitize category field."""
    return sanitize_text(value, MAX_CATEGORY_LENGTH)


def sanitize_supplier(value: str) -> str:
    """Sanitize supplier/vendor field."""
    return sanitize_text(value, MAX_SUPPLIER_LENGTH)


# ============================================================================
# EXPORT SAFETY (Excel/CSV Injection Prevention)
# ============================================================================

# Characters that trigger formula execution in Excel/Sheets
FORMULA_TRIGGERS = ['=', '+', '-', '@', '\t', '\r']


def escape_csv_value(value: str) -> str:
    """
    Escape a value for safe CSV export.
    
    Prevents formula injection by prefixing dangerous values with a single quote.
    This technique is recommended by OWASP for spreadsheet injection prevention.
    """
    if not value:
        return value
    
    value = str(value)
    
    # Check if first character is a formula trigger
    if value and value[0] in FORMULA_TRIGGERS:
        # Prefix with single quote to prevent formula execution
        return "'" + value
    
    return value


def escape_csv_row(row: List[str]) -> List[str]:
    """Escape all values in a CSV row."""
    return [escape_csv_value(v) for v in row]


def make_csv_safe(data: List[List[str]]) -> List[List[str]]:
    """Make entire CSV data safe for export."""
    return [escape_csv_row(row) for row in data]


# ============================================================================
# INPUT VALIDATION
# ============================================================================

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_date_format(value: str) -> bool:
    """Validate date is in expected format (YYYY-MM-DD or DD/MM/YYYY)."""
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',      # YYYY-MM-DD
        r'^\d{2}/\d{2}/\d{4}$',      # DD/MM/YYYY
    ]
    return any(re.match(p, value) for p in patterns)


def validate_numeric(value: Any) -> bool:
    """Validate value is numeric."""
    try:
        float(str(value).replace(',', '.').replace(' ', ''))
        return True
    except (ValueError, TypeError):
        return False


def validate_category_text(value: str) -> bool:
    """
    Validate category is plain text (not formula or script).
    Categories should never start with = or contain scripts.
    """
    if not value:
        return True
    
    value = str(value).strip()
    
    # Reject formula triggers
    if value and value[0] in FORMULA_TRIGGERS:
        logger.warning(f"Category rejected: starts with formula trigger")
        return False
    
    # Reject HTML/script tags
    if re.search(r'<[^>]*script|javascript:|on\w+=', value, re.IGNORECASE):
        logger.warning(f"Category rejected: contains script")
        return False
    
    return True


# ============================================================================
# BATCH SANITIZATION
# ============================================================================

def sanitize_transaction_dict(tx: dict) -> dict:
    """Sanitize all fields in a transaction dictionary."""
    sanitized = tx.copy()
    
    if 'description' in sanitized:
        sanitized['description'] = sanitize_description(str(sanitized['description']))
    
    if 'category' in sanitized:
        sanitized['category'] = sanitize_category(str(sanitized['category']))
    
    if 'supplier' in sanitized or 'fornecedor' in sanitized:
        key = 'supplier' if 'supplier' in sanitized else 'fornecedor'
        sanitized[key] = sanitize_supplier(str(sanitized[key]))
    
    if 'cost_center' in sanitized or 'centro_custo' in sanitized:
        key = 'cost_center' if 'cost_center' in sanitized else 'centro_custo'
        sanitized[key] = sanitize_text(str(sanitized[key]), 100)
    
    return sanitized


def sanitize_transaction_list(transactions: List[dict]) -> List[dict]:
    """Sanitize all transactions in a list."""
    return [sanitize_transaction_dict(tx) for tx in transactions]


# ============================================================================
# XSS PREVENTION (for web display)
# ============================================================================

HTML_ESCAPE_TABLE = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
}


def escape_html(value: str) -> str:
    """Escape HTML special characters to prevent XSS."""
    if not value:
        return value
    
    for char, escape in HTML_ESCAPE_TABLE.items():
        value = value.replace(char, escape)
    
    return value
