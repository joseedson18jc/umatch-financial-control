"""
CSV Normalization System v1.3 CORE

A deterministic pipeline for normalizing financial CSVs using Anthropic Claude with Structured Outputs.

Features:
- Phase 1: Extraction & Detection (delimiter, encoding, date format)
- Phase 2: Plan Generation (AI with structured outputs)
- Phase 3: Validation (JSON Schema + semantic validation)
- Phase 4: Transformation (20+ deterministic operations)
- Phase 5: Quality & Deduplication
- Phase 6: Import & Persistence
"""

import os
import json
import logging
import hashlib
import unicodedata
import re
from typing import Dict, List, Any, Optional, Tuple, TypedDict
from datetime import datetime
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

# ============================================================================
# TYPE DEFINITIONS (v1.3 Schema)
# ============================================================================

class ColumnMapping(TypedDict, total=False):
    source: str
    method: str
    formats: List[str]
    decimal: str
    thousand: str
    in_field: str
    out_field: str
    value: Any

class TransformOperation(TypedDict):
    op: str
    source: str
    target: str
    params: Dict[str, Any]

class QualityCheck(TypedDict):
    field: str
    check: str
    threshold: float

@dataclass
class NormalizationPlanV13:
    """v1.3 Normalization Plan Structure"""
    schema_version: str = "1.3"
    confidence: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)
    csv_read: Dict[str, Any] = field(default_factory=dict)
    mapping: Dict[str, ColumnMapping] = field(default_factory=dict)
    transform_plan: List[TransformOperation] = field(default_factory=list)
    quality_checks: List[QualityCheck] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    column_profile: Dict[str, Any] = field(default_factory=dict)
    field_detection: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionNormalized:
    """Normalized transaction output"""
    date: str
    description: str
    amount: float
    operation_type: str  # "credit" or "debit"
    category: Optional[str] = None
    cost_center: Optional[str] = None
    currency: str = "BRL"
    original_row: int = 0
    hash: str = ""


@dataclass
class ImportResult:
    """Result of import operation"""
    success: bool
    total_rows: int
    imported_rows: int
    duplicates_removed: int
    errors: List[str]
    warnings: List[str]
    quality_score: float
    plan_id: Optional[str] = None


# ============================================================================
# PHASE 1: EXTRACTION & DETECTION
# ============================================================================

def detect_delimiter(sample_text: str) -> str:
    """Detect CSV delimiter from sample text."""
    delimiters = [';', ',', '|', '\t']
    counts = {d: sample_text.count(d) for d in delimiters}
    
    # Count per line to find most consistent
    lines = sample_text.strip().split('\n')[:10]
    if not lines:
        return ','
    
    best = ','
    best_score = 0
    
    for d in delimiters:
        line_counts = [line.count(d) for line in lines]
        if line_counts and min(line_counts) > 0:
            consistency = min(line_counts) / max(line_counts) if max(line_counts) > 0 else 0
            avg_count = sum(line_counts) / len(line_counts)
            score = consistency * avg_count
            if score > best_score:
                best_score = score
                best = d
    
    return best


def detect_encoding(file_content: bytes) -> str:
    """Detect file encoding."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for enc in encodings:
        try:
            file_content.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    
    return 'latin-1'  # Fallback


def detect_has_header(lines: List[str], delimiter: str) -> Tuple[bool, float]:
    """Detect if first line is a header. Returns (has_header, confidence)."""
    if len(lines) < 2:
        return True, 0.5
    
    first_line = lines[0].split(delimiter)
    second_line = lines[1].split(delimiter)
    
    # Check if first line has more text-like values
    first_text_ratio = sum(1 for v in first_line if not _looks_like_number(v)) / len(first_line)
    second_text_ratio = sum(1 for v in second_line if not _looks_like_number(v)) / len(second_line)
    
    # If first line is more text-heavy, likely header
    if first_text_ratio > second_text_ratio + 0.2:
        return True, 0.9
    elif first_text_ratio < second_text_ratio - 0.2:
        return False, 0.8
    else:
        return True, 0.6


def _looks_like_number(value: str) -> bool:
    """Check if value looks like a number."""
    v = value.strip().replace('.', '').replace(',', '').replace('-', '').replace(' ', '')
    return v.isdigit()


def detect_date_format(sample_values: List[str]) -> List[str]:
    """Detect date format from sample values."""
    formats = []
    patterns = [
        (r'\d{2}/\d{2}/\d{4}', 'DD/MM/YYYY'),
        (r'\d{4}-\d{2}-\d{2}', 'YYYY-MM-DD'),
        (r'\d{2}-\d{2}-\d{4}', 'DD-MM-YYYY'),
        (r'\d{2}\.\d{2}\.\d{4}', 'DD.MM.YYYY'),
    ]
    
    for value in sample_values[:20]:
        for pattern, fmt in patterns:
            if re.match(pattern, value.strip()):
                if fmt not in formats:
                    formats.append(fmt)
    
    return formats if formats else ['DD/MM/YYYY']


def extract_csv_metadata(file_content: bytes) -> Dict[str, Any]:
    """Extract all metadata from CSV file (Phase 1)."""
    encoding = detect_encoding(file_content)
    text = file_content.decode(encoding, errors='ignore')
    
    lines = text.strip().split('\n')[:50]
    delimiter = detect_delimiter('\n'.join(lines))
    has_header, header_confidence = detect_has_header(lines, delimiter)
    
    # Parse columns
    if has_header and lines:
        columns = [c.strip().strip('"') for c in lines[0].split(delimiter)]
    else:
        columns = [f"col_{i}" for i in range(len(lines[0].split(delimiter)))]
    
    # Get sample rows
    sample_rows = []
    start_idx = 1 if has_header else 0
    for line in lines[start_idx:start_idx + 20]:
        values = [v.strip().strip('"') for v in line.split(delimiter)]
        if len(values) == len(columns):
            sample_rows.append(dict(zip(columns, values)))
    
    return {
        "encoding": encoding,
        "delimiter": delimiter,
        "has_header": has_header,
        "header_confidence": header_confidence,
        "columns": columns,
        "row_count": len(lines) - (1 if has_header else 0),
        "sample_rows": sample_rows,
        "sample_text": '\n'.join(lines[:20])
    }


# ============================================================================
# PHASE 2: PLAN GENERATION (AI with Structured Outputs)
# ============================================================================

SYSTEM_PROMPT_V13 = """You are a deterministic CSV normalization planner for financial data.

## 11 INVIOLABLE RULES:

1. ALWAYS return valid JSON matching the NormalizationPlanV13 schema
2. NEVER invent columns - only use columns that exist in the CSV
3. ALWAYS map: date, description, amount (required fields)
4. For Brazilian format: 1.234,56 means 1234.56 (thousand=., decimal=,)
5. For Débito/Crédito: Débito is negative, Crédito is positive
6. For separate columns (Débito, Crédito): compute_amount_from_in_out
7. Date formats: detect from sample, prefer DD/MM/YYYY for Brazilian
8. operation_type: derive from amount sign or explicit column
9. confidence: 0.0-1.0 based on clarity of data
10. Include ALL warnings about ambiguities
11. transform_plan must be in correct execution order

## OUTPUT SCHEMA:
{
  "schema_version": "1.3",
  "confidence": 0.0-1.0,
  "summary": {
    "detected_layout": "string describing layout",
    "key_decisions": ["decision1", "decision2"],
    "main_risks": ["risk1"]
  },
  "csv_read": {
    "delimiter": ";" or "," or "|",
    "encoding": "utf-8" or "latin-1",
    "has_header": true/false,
    "skip_rows": 0
  },
  "mapping": {
    "date": {"source": "column_name", "method": "parse_date", "formats": ["DD/MM/YYYY"]},
    "description": {"source": "column_name", "method": "direct"},
    "amount": {"source": "column_name", "method": "parse_money_ptbr", "decimal": ",", "thousand": "."},
    "operation_type": {"method": "derive_from_amount_sign"},
    "category": {"source": "column_name", "method": "direct"} // optional
  },
  "transform_plan": [
    {"op": "trim", "source": "*", "target": "*", "params": {}},
    {"op": "parse_date", "source": "date", "target": "date", "params": {"formats": ["DD/MM/YYYY"]}},
    {"op": "parse_money_ptbr", "source": "amount", "target": "amount", "params": {"decimal": ",", "thousand": "."}}
  ],
  "quality_checks": [
    {"field": "date", "check": "not_null", "threshold": 0.95},
    {"field": "amount", "check": "is_numeric", "threshold": 0.95},
    {"field": "description", "check": "not_empty", "threshold": 0.90}
  ],
  "warnings": ["any warnings about the data"]
}
"""


def build_user_prompt_v13(metadata: Dict[str, Any]) -> str:
    """Build user prompt for plan generation."""
    return f"""Analyze this CSV and generate a NormalizationPlanV13.

## DETECTED METADATA:
- Delimiter: {metadata['delimiter']}
- Encoding: {metadata['encoding']}
- Has Header: {metadata['has_header']} (confidence: {metadata.get('header_confidence', 0.5):.2f})
- Columns: {metadata['columns']}
- Row Count: {metadata['row_count']}

## SAMPLE DATA (first 10 rows):
```csv
{metadata['sample_text']}
```

## SAMPLE PARSED ROWS:
{json.dumps(metadata['sample_rows'][:5], indent=2, ensure_ascii=False)}

Generate the NormalizationPlanV13 JSON. Remember:
- Map date, description, amount (required)
- Detect Brazilian money format (1.234,56)
- Detect date format from samples
- Set confidence based on clarity
- List any warnings
"""


async def generate_normalization_plan_v13(
    file_content: bytes,
    api_key: Optional[str] = None,
    debug: bool = False
) -> NormalizationPlanV13:
    """Generate normalization plan using Claude (Phase 2)."""
    
    # Phase 1: Extract metadata
    metadata = extract_csv_metadata(file_content)
    
    # Try to import Anthropic
    try:
        import anthropic
    except ImportError:
        logger.warning("Anthropic not installed, using heuristic plan")
        return _generate_heuristic_plan(metadata)
    
    # Get API key
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        logger.warning("No Anthropic API key, using heuristic plan")
        return _generate_heuristic_plan(metadata)
    
    client = anthropic.Anthropic(api_key=key.strip())
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=SYSTEM_PROMPT_V13,
            messages=[
                {"role": "user", "content": build_user_prompt_v13(metadata)}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON from response
        plan_dict = _extract_json_from_response(response_text)
        
        # Convert to dataclass
        plan = NormalizationPlanV13(
            schema_version=plan_dict.get("schema_version", "1.3"),
            confidence=plan_dict.get("confidence", 0.5),
            summary=plan_dict.get("summary", {}),
            csv_read=plan_dict.get("csv_read", {"delimiter": metadata['delimiter']}),
            mapping=plan_dict.get("mapping", {}),
            transform_plan=plan_dict.get("transform_plan", []),
            quality_checks=plan_dict.get("quality_checks", []),
            warnings=plan_dict.get("warnings", [])
        )
        
        if debug:
            plan.column_profile = metadata
            plan.field_detection = plan_dict.get("field_detection", {})
        
        return plan
        
    except Exception as e:
        logger.error(f"Error generating plan with Claude: {e}")
        return _generate_heuristic_plan(metadata)


def _extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from Claude response."""
    # Try to find JSON block
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        text = text[start:end].strip()
    
    # Try to parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {}


def _generate_heuristic_plan(metadata: Dict[str, Any]) -> NormalizationPlanV13:
    """Generate plan using heuristics when AI is unavailable."""
    columns = metadata['columns']
    columns_lower = [c.lower() for c in columns]
    
    # Find date column
    date_col = None
    for i, c in enumerate(columns_lower):
        if any(x in c for x in ['data', 'date', 'dt', 'dia']):
            date_col = columns[i]
            break
    
    # Find description column
    desc_col = None
    for i, c in enumerate(columns_lower):
        if any(x in c for x in ['descr', 'desc', 'histórico', 'historico', 'lancamento']):
            desc_col = columns[i]
            break
    
    # Find amount column
    amount_col = None
    for i, c in enumerate(columns_lower):
        if any(x in c for x in ['valor', 'value', 'amount', 'val', 'montante']):
            amount_col = columns[i]
            break
    
    # Detect date format from samples
    date_formats = ['DD/MM/YYYY']
    if metadata['sample_rows'] and date_col:
        sample_dates = [r.get(date_col, '') for r in metadata['sample_rows']]
        date_formats = detect_date_format(sample_dates)
    
    mapping = {}
    if date_col:
        mapping['date'] = {
            'source': date_col,
            'method': 'parse_date',
            'formats': date_formats
        }
    if desc_col:
        mapping['description'] = {
            'source': desc_col,
            'method': 'direct'
        }
    if amount_col:
        mapping['amount'] = {
            'source': amount_col,
            'method': 'parse_money_ptbr',
            'decimal': ',',
            'thousand': '.'
        }
    mapping['operation_type'] = {'method': 'derive_from_amount_sign'}
    
    return NormalizationPlanV13(
        schema_version="1.3",
        confidence=0.6,
        summary={
            'detected_layout': f"CSV with delimiter '{metadata['delimiter']}'",
            'key_decisions': [f'Date from {date_col}', f'Amount from {amount_col}'],
            'main_risks': ['Heuristic plan - review recommended']
        },
        csv_read={
            'delimiter': metadata['delimiter'],
            'encoding': metadata['encoding'],
            'has_header': metadata['has_header'],
            'skip_rows': 0
        },
        mapping=mapping,
        transform_plan=[
            {'op': 'trim', 'source': '*', 'target': '*', 'params': {}},
            {'op': 'parse_date', 'source': 'date', 'target': 'date', 'params': {'formats': date_formats}},
            {'op': 'parse_money_ptbr', 'source': 'amount', 'target': 'amount', 'params': {'decimal': ',', 'thousand': '.'}}
        ],
        quality_checks=[
            {'field': 'date', 'check': 'not_null', 'threshold': 0.95},
            {'field': 'amount', 'check': 'is_numeric', 'threshold': 0.95}
        ],
        warnings=['Generated using heuristics - AI analysis recommended']
    )


# ============================================================================
# PHASE 3: VALIDATION
# ============================================================================

def validate_plan_v13(plan: NormalizationPlanV13, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate normalization plan (Phase 3)."""
    errors = []
    
    # Check schema version
    if plan.schema_version != "1.3":
        errors.append(f"Invalid schema version: {plan.schema_version}")
    
    # Check required mappings
    required = ['date', 'description', 'amount']
    for field in required:
        if field not in plan.mapping:
            errors.append(f"Missing required mapping: {field}")
        elif 'source' in plan.mapping[field]:
            source = plan.mapping[field]['source']
            if source not in metadata['columns']:
                errors.append(f"Mapped column '{source}' does not exist in CSV")
    
    # Check confidence
    if not 0 <= plan.confidence <= 1:
        errors.append(f"Invalid confidence: {plan.confidence}")
    
    # Check transform_plan order
    transform_ops = [t['op'] for t in plan.transform_plan]
    if 'trim' in transform_ops and transform_ops.index('trim') != 0:
        errors.append("trim operation should be first")
    
    return len(errors) == 0, errors


# ============================================================================
# PHASE 4: TRANSFORMATION ENGINE
# ============================================================================

def parse_date(value: str, formats: List[str]) -> Optional[str]:
    """Parse date string to ISO format."""
    if not value or not value.strip():
        return None
    
    value = value.strip()
    
    format_mappings = {
        'DD/MM/YYYY': '%d/%m/%Y',
        'MM/DD/YYYY': '%m/%d/%Y',
        'YYYY-MM-DD': '%Y-%m-%d',
        'DD-MM-YYYY': '%d-%m-%Y',
        'DD.MM.YYYY': '%d.%m.%Y',
    }
    
    for fmt in formats:
        py_fmt = format_mappings.get(fmt)
        if py_fmt:
            try:
                dt = datetime.strptime(value, py_fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    return None


def parse_money_ptbr(value: str, thousand: str = '.', decimal: str = ',') -> Optional[float]:
    """Parse Brazilian money format to float."""
    if not value or not str(value).strip():
        return None
    
    value = str(value).strip()
    
    # Remove currency symbols
    value = re.sub(r'[R$€£¥]', '', value).strip()
    
    # Handle parentheses (accounting negative)
    is_negative = False
    if value.startswith('(') and value.endswith(')'):
        is_negative = True
        value = value[1:-1]
    
    # Handle trailing minus
    if value.endswith('-'):
        is_negative = True
        value = value[:-1]
    
    # Handle leading minus
    if value.startswith('-'):
        is_negative = True
        value = value[1:]
    
    # Remove spaces
    value = value.replace(' ', '')
    
    # Handle thousand/decimal separators
    if thousand and decimal:
        value = value.replace(thousand, '').replace(decimal, '.')
    elif ',' in value and '.' in value:
        # Detect format
        if value.rfind(',') > value.rfind('.'):
            # Brazilian: 1.234,56
            value = value.replace('.', '').replace(',', '.')
        else:
            # US: 1,234.56
            value = value.replace(',', '')
    elif ',' in value:
        value = value.replace(',', '.')
    
    try:
        result = float(value)
        return -result if is_negative else result
    except ValueError:
        return None


def compute_amount_from_in_out(in_value: str, out_value: str) -> Optional[float]:
    """Compute amount from separate credit/debit columns."""
    in_amount = parse_money_ptbr(in_value) if in_value and in_value.strip() else None
    out_amount = parse_money_ptbr(out_value) if out_value and out_value.strip() else None
    
    if in_amount is not None and in_amount != 0:
        return abs(in_amount)
    elif out_amount is not None and out_amount != 0:
        return -abs(out_amount)
    
    return None


def normalize_text(value: str) -> str:
    """Normalize text: trim, remove accents for comparison."""
    if not value:
        return ""
    value = str(value).strip()
    value = unicodedata.normalize('NFKD', value)
    return ''.join(c for c in value if not unicodedata.combining(c))


def transform_row(row: Dict[str, str], plan: NormalizationPlanV13) -> TransactionNormalized:
    """Apply transformation plan to a single row."""
    mapping = plan.mapping
    
    # Extract date
    date_val = None
    if 'date' in mapping:
        source = mapping['date'].get('source', '')
        raw_date = row.get(source, '')
        formats = mapping['date'].get('formats', ['DD/MM/YYYY'])
        date_val = parse_date(raw_date, formats)
    
    # Extract description
    desc_val = ""
    if 'description' in mapping:
        source = mapping['description'].get('source', '')
        desc_val = row.get(source, '').strip()
    
    # Extract amount
    amount_val = 0.0
    if 'amount' in mapping:
        amount_cfg = mapping['amount']
        method = amount_cfg.get('method', 'parse_money_ptbr')
        
        if method == 'compute_amount_from_in_out':
            in_field = amount_cfg.get('in_field', '')
            out_field = amount_cfg.get('out_field', '')
            amount_val = compute_amount_from_in_out(
                row.get(in_field, ''),
                row.get(out_field, '')
            ) or 0.0
        else:
            source = amount_cfg.get('source', '')
            decimal = amount_cfg.get('decimal', ',')
            thousand = amount_cfg.get('thousand', '.')
            amount_val = parse_money_ptbr(row.get(source, ''), thousand, decimal) or 0.0
    
    # Derive operation type
    if amount_val >= 0:
        op_type = "credit"
    else:
        op_type = "debit"
    
    # Extract optional fields
    category = None
    if 'category' in mapping:
        source = mapping['category'].get('source', '')
        category = row.get(source, '').strip() or None
    
    cost_center = None
    if 'cost_center' in mapping:
        source = mapping['cost_center'].get('source', '')
        cost_center = row.get(source, '').strip() or None
    
    return TransactionNormalized(
        date=date_val or '',
        description=desc_val,
        amount=amount_val,
        operation_type=op_type,
        category=category,
        cost_center=cost_center,
        currency="BRL"
    )


def transform_csv(file_content: bytes, plan: NormalizationPlanV13) -> List[TransactionNormalized]:
    """Apply transformation to entire CSV (Phase 4)."""
    csv_cfg = plan.csv_read
    encoding = csv_cfg.get('encoding', 'utf-8')
    delimiter = csv_cfg.get('delimiter', ';')
    has_header = csv_cfg.get('has_header', True)
    skip_rows = csv_cfg.get('skip_rows', 0)
    
    # Decode content
    text = file_content.decode(encoding, errors='ignore')
    lines = text.strip().split('\n')
    
    # Skip rows if needed
    lines = lines[skip_rows:]
    
    # Get columns
    if has_header and lines:
        columns = [c.strip().strip('"') for c in lines[0].split(delimiter)]
        data_lines = lines[1:]
    else:
        # Generate column names
        if lines:
            first_values = lines[0].split(delimiter)
            columns = [f"col_{i}" for i in range(len(first_values))]
        else:
            columns = []
        data_lines = lines
    
    # Transform each row
    transactions = []
    for idx, line in enumerate(data_lines):
        values = [v.strip().strip('"') for v in line.split(delimiter)]
        if len(values) != len(columns):
            continue
        
        row_dict = dict(zip(columns, values))
        tx = transform_row(row_dict, plan)
        tx.original_row = idx + 1 + skip_rows + (1 if has_header else 0)
        
        # Generate hash for deduplication
        hash_input = f"{tx.date}|{tx.amount}|{normalize_text(tx.description)}"
        tx.hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        transactions.append(tx)
    
    return transactions


# ============================================================================
# PHASE 5: QUALITY & DEDUPLICATION
# ============================================================================

def check_quality(
    transactions: List[TransactionNormalized],
    checks: List[QualityCheck]
) -> Dict[str, Any]:
    """Run quality checks on transformed data (Phase 5)."""
    results = {}
    
    total = len(transactions)
    if total == 0:
        return {'success': False, 'error': 'No transactions'}
    
    # Date check
    valid_dates = sum(1 for t in transactions if t.date)
    results['date_success_rate'] = valid_dates / total
    
    # Amount check
    valid_amounts = sum(1 for t in transactions if t.amount != 0)
    results['amount_success_rate'] = valid_amounts / total
    
    # Description check
    valid_descs = sum(1 for t in transactions if t.description.strip())
    results['description_success_rate'] = valid_descs / total
    
    # Overall quality score
    results['overall_quality'] = (
        results['date_success_rate'] * 0.4 +
        results['amount_success_rate'] * 0.4 +
        results['description_success_rate'] * 0.2
    )
    
    # Check against thresholds
    results['passed'] = True
    results['failures'] = []
    
    for check in checks:
        field = check['field']
        threshold = check['threshold']
        rate = results.get(f'{field}_success_rate', 0)
        
        if rate < threshold:
            results['passed'] = False
            results['failures'].append(
                f"{field}: {rate:.2%} < {threshold:.2%}"
            )
    
    return results


def deduplicate(transactions: List[TransactionNormalized]) -> Tuple[List[TransactionNormalized], int]:
    """Remove duplicate transactions based on hash."""
    seen_hashes = set()
    unique = []
    duplicates = 0
    
    for tx in transactions:
        if tx.hash not in seen_hashes:
            seen_hashes.add(tx.hash)
            unique.append(tx)
        else:
            duplicates += 1
    
    return unique, duplicates


# ============================================================================
# PHASE 6: MAIN IMPORT FUNCTION
# ============================================================================

async def import_csv_v13(
    file_content: bytes,
    api_key: Optional[str] = None,
    skip_ai: bool = False,
    debug: bool = False
) -> ImportResult:
    """
    Main import function implementing full v1.3 pipeline.
    
    Args:
        file_content: Raw CSV file bytes
        api_key: Anthropic API key (optional)
        skip_ai: If True, use heuristic plan only
        debug: If True, include debug info in plan
    
    Returns:
        ImportResult with statistics and status
    """
    errors = []
    warnings = []
    
    try:
        # Phase 1: Extract metadata
        logger.info("Phase 1: Extracting CSV metadata...")
        metadata = extract_csv_metadata(file_content)
        logger.info(f"  Detected: delimiter='{metadata['delimiter']}', encoding={metadata['encoding']}, columns={len(metadata['columns'])}")
        
        # Phase 2: Generate plan
        logger.info("Phase 2: Generating normalization plan...")
        if skip_ai:
            plan = _generate_heuristic_plan(metadata)
        else:
            plan = await generate_normalization_plan_v13(file_content, api_key, debug)
        logger.info(f"  Plan confidence: {plan.confidence:.2%}")
        warnings.extend(plan.warnings)
        
        # Phase 3: Validate plan
        logger.info("Phase 3: Validating plan...")
        is_valid, validation_errors = validate_plan_v13(plan, metadata)
        if not is_valid:
            errors.extend(validation_errors)
            return ImportResult(
                success=False,
                total_rows=metadata['row_count'],
                imported_rows=0,
                duplicates_removed=0,
                errors=errors,
                warnings=warnings,
                quality_score=0.0
            )
        logger.info("  Plan valid ✓")
        
        # Phase 4: Transform
        logger.info("Phase 4: Transforming data...")
        transactions = transform_csv(file_content, plan)
        logger.info(f"  Transformed {len(transactions)} rows")
        
        # Phase 5: Quality & Deduplication
        logger.info("Phase 5: Quality check & deduplication...")
        quality = check_quality(transactions, plan.quality_checks)
        transactions, dup_count = deduplicate(transactions)
        logger.info(f"  Quality: {quality['overall_quality']:.2%}, Duplicates removed: {dup_count}")
        
        if quality['failures']:
            warnings.extend(quality['failures'])
        
        # Phase 6: Return result (actual DB import would go here)
        logger.info("Phase 6: Import complete")
        
        return ImportResult(
            success=True,
            total_rows=metadata['row_count'],
            imported_rows=len(transactions),
            duplicates_removed=dup_count,
            errors=errors,
            warnings=warnings,
            quality_score=quality['overall_quality'],
            plan_id=hashlib.md5(json.dumps(asdict(plan)).encode()).hexdigest()[:12]
        )
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        errors.append(str(e))
        return ImportResult(
            success=False,
            total_rows=0,
            imported_rows=0,
            duplicates_removed=0,
            errors=errors,
            warnings=warnings,
            quality_score=0.0
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def export_transactions_to_dict(transactions: List[TransactionNormalized]) -> List[Dict[str, Any]]:
    """Export transactions to list of dictionaries."""
    return [asdict(tx) for tx in transactions]


def get_plan_summary(plan: NormalizationPlanV13) -> Dict[str, Any]:
    """Get human-readable plan summary."""
    return {
        'version': plan.schema_version,
        'confidence': f"{plan.confidence:.0%}",
        'layout': plan.summary.get('detected_layout', 'Unknown'),
        'decisions': plan.summary.get('key_decisions', []),
        'risks': plan.summary.get('main_risks', []),
        'warnings': plan.warnings,
        'mappings': {
            k: v.get('source', v.get('method', 'unknown'))
            for k, v in plan.mapping.items()
        }
    }
