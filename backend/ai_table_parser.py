"""
AI-powered CSV table parser using Anthropic's Claude API.

This service intelligently analyzes CSV files to:
1. Detect column mappings automatically
2. Identify the type of financial data
3. Suggest appropriate category mappings
4. Adapt to different table formats
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import Anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not installed. AI table parsing will be unavailable.")


def get_anthropic_client(api_key: Optional[str] = None) -> Optional[Any]:
    """Get Anthropic client with provided or environment API key."""
    if not ANTHROPIC_AVAILABLE:
        return None
    
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    
    return anthropic.Anthropic(api_key=key.strip())


def analyze_csv_structure(
    csv_sample: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze CSV structure and detect column mappings using Claude.
    
    Args:
        csv_sample: First 20-50 rows of the CSV as a string
        api_key: Anthropic API key (optional, uses env var if not provided)
    
    Returns:
        Dictionary with detected mappings and suggestions
    """
    client = get_anthropic_client(api_key)
    
    if not client:
        return {
            "success": False,
            "error": "Anthropic client not available. Please install 'anthropic' package and provide API key.",
            "column_mappings": {},
            "suggestions": []
        }
    
    prompt = f"""Analyze this CSV financial data sample and identify the column structure.

CSV SAMPLE:
```
{csv_sample[:4000]}
```

Please analyze and return a JSON object with:

1. "detected_format": The likely source/format (e.g., "Conta Azul", "Excel Export", "Bank Statement", etc.)

2. "column_mappings": Map each CSV column to our standard columns:
   - "date_column": Column containing dates (e.g., "Data de competência")
   - "value_column": Column containing monetary values (e.g., "Valor (R$)")
   - "type_column": Column indicating Entrada/Saída, Débito/Crédito (e.g., "Tipo")
   - "cost_center_column": Column with cost center (e.g., "Centro de Custo 1")
   - "supplier_column": Column with supplier/client name (e.g., "Nome do fornecedor/cliente")
   - "description_column": Column with transaction description
   - "category_column": Column with account category (e.g., "Plano de contas")

3. "date_format": Detected date format (e.g., "DD/MM/YYYY", "YYYY-MM-DD")

4. "value_format": Value format ("BR" for 1.234,56 or "US" for 1,234.56)

5. "encoding_hint": Likely encoding ("utf-8", "latin-1", "cp1252")

6. "separator": Detected separator ("," or ";")

7. "suggestions": List of any issues or recommendations for processing

Return ONLY valid JSON, no explanation text.
"""

    try:
        logger.info("Sending CSV structure analysis request to Claude...")
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response_text = message.content[0].text
        
        # Try to extract JSON from response
        try:
            # Handle cases where response might have markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            result["success"] = True
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            return {
                "success": False,
                "error": f"Failed to parse AI response: {e}",
                "raw_response": response_text[:500],
                "column_mappings": {},
                "suggestions": []
            }
            
    except Exception as e:
        logger.error(f"Error calling Anthropic API: {e}")
        return {
            "success": False,
            "error": str(e),
            "column_mappings": {},
            "suggestions": []
        }


def suggest_category_mappings(
    transactions_sample: List[Dict[str, Any]],
    existing_mappings: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Suggest new category mappings for unmapped transactions using Claude.
    
    Args:
        transactions_sample: Sample of unmapped transactions
        existing_mappings: Current mapping rules
        api_key: Anthropic API key
    
    Returns:
        List of suggested new mappings
    """
    client = get_anthropic_client(api_key)
    
    if not client:
        return []
    
    # Prepare transaction summary
    tx_summary = []
    for tx in transactions_sample[:30]:  # Limit to 30 transactions
        tx_summary.append({
            "cost_center": tx.get("centro_custo", ""),
            "supplier": tx.get("fornecedor", ""),
            "description": tx.get("descricao", "")[:100],
            "value": tx.get("valor", 0)
        })
    
    # Prepare existing mappings summary
    mapping_summary = []
    for m in existing_mappings[:50]:  # Limit to 50 mappings
        mapping_summary.append({
            "grupo": m.get("grupo_financeiro", ""),
            "centro_custo": m.get("centro_custo", ""),
            "fornecedor": m.get("fornecedor_cliente", ""),
            "linha_pl": m.get("linha_pl", ""),
            "tipo": m.get("tipo", "")
        })
    
    prompt = f"""Analyze these unmapped financial transactions and suggest category mappings.

UNMAPPED TRANSACTIONS:
{json.dumps(tx_summary, indent=2, ensure_ascii=False)}

EXISTING MAPPINGS (for reference):
{json.dumps(mapping_summary, indent=2, ensure_ascii=False)}

Based on the patterns, suggest new mappings for the unmapped transactions.
Return a JSON array of suggested mappings with this structure:

[
  {{
    "grupo_financeiro": "Group name (e.g., 'COGS', 'SG&A', 'Receita')",
    "centro_custo": "Cost center to match",
    "fornecedor_cliente": "Supplier pattern to match",
    "linha_pl": "P&L line number (use existing patterns)",
    "tipo": "Receita|Custo|Despesa",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation"
  }}
]

Return ONLY valid JSON array, no explanation text.
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        suggestions = json.loads(response_text)
        
        # Filter high-confidence suggestions
        return [s for s in suggestions if s.get("confidence", 0) >= 0.6]
        
    except Exception as e:
        logger.error(f"Error getting mapping suggestions from Claude: {e}")
        return []


def detect_csv_format(file_content: bytes, api_key: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Detect CSV encoding, separator, and format using a combination of heuristics and AI.
    
    Returns:
        Tuple of (encoding, separator, date_format)
    """
    # Try to decode with different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    decoded = None
    detected_encoding = 'utf-8'
    
    for enc in encodings:
        try:
            decoded = file_content.decode(enc)
            detected_encoding = enc
            break
        except UnicodeDecodeError:
            continue
    
    if not decoded:
        decoded = file_content.decode('latin-1', errors='ignore')
        detected_encoding = 'latin-1'
    
    # Get first few lines for analysis
    lines = decoded.split('\n')[:20]
    sample = '\n'.join(lines)
    
    # Heuristic: detect separator
    first_line = lines[0] if lines else ""
    semicolon_count = first_line.count(';')
    comma_count = first_line.count(',')
    separator = ';' if semicolon_count > comma_count else ','
    
    # If API key provided, use AI for deeper analysis
    if api_key and ANTHROPIC_AVAILABLE:
        result = analyze_csv_structure(sample, api_key)
        if result.get("success"):
            detected_encoding = result.get("encoding_hint", detected_encoding)
            separator = result.get("separator", separator)
            return (detected_encoding, separator, result.get("date_format", "DD/MM/YYYY"))
    
    # Default date format for Brazilian CSVs
    return (detected_encoding, separator, "DD/MM/YYYY")
