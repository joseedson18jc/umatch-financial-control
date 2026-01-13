"""
Conta Azul CSV Configuration and Mapping Templates

Pre-configured templates for:
- Conta Azul extrato CSV format detection
- 33 P&L mapping rules (Receita, COGS, SG&A, etc.)
- Financial group definitions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import hashlib
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONTA AZUL CSV FORMAT CONFIGURATION
# ============================================================================

CONTA_AZUL_CONFIG = {
    "name": "Conta Azul - Extrato Financeiro",
    "version": "1.0",
    "delimiter": ";",
    "encoding": "utf-8",
    "date_format": "DD/MM/YYYY",
    "decimal_separator": ",",
    "thousand_separator": ".",
    "currency": "BRL",
    
    # Expected columns (Portuguese names from Conta Azul export)
    "expected_columns": [
        "Data de competência",
        "Centro de custo", 
        "Fornecedor/Cliente",
        "Descrição",
        "Valor",
        "Tipo de operação",
        "Categoria",
    ],
    
    # Column mappings to normalized names
    "column_mapping": {
        "Data de competência": "date",
        "Data competência": "date",
        "Data": "date",
        "Centro de custo": "cost_center",
        "Centro custo": "cost_center",
        "Fornecedor/Cliente": "supplier",
        "Fornecedor": "supplier",
        "Cliente": "supplier",
        "Descrição": "description",
        "Descricao": "description",
        "Valor": "amount",
        "Valor (R$)": "amount",
        "Tipo de operação": "operation_type",
        "Tipo operação": "operation_type",
        "Tipo": "operation_type",
        "Categoria": "category",
    },
    
    # Fingerprint for template matching
    "fingerprint_hash": "conta_azul_extrato_v1"
}


# ============================================================================
# FINANCIAL GROUP DEFINITIONS
# ============================================================================

@dataclass
class FinancialGroup:
    """Financial group for P&L mapping."""
    id: str
    name: str
    type: str  # "revenue", "cost", "expense"
    pnl_section: str  # "revenue", "cogs", "gross_profit", "opex", "ebitda"
    calculation_rule: Optional[str] = None


FINANCIAL_GROUPS = {
    # Revenue Groups
    "receita_google": FinancialGroup(
        id="receita_google",
        name="Receita Google Play",
        type="revenue",
        pnl_section="revenue",
        calculation_rule="net_to_gross_85"  # Receita Bruta = Líquida / 0.85
    ),
    "receita_apple": FinancialGroup(
        id="receita_apple", 
        name="Receita App Store",
        type="revenue",
        pnl_section="revenue",
        calculation_rule="net_to_gross_85"
    ),
    "receita_rendimentos": FinancialGroup(
        id="receita_rendimentos",
        name="Rendimentos de Aplicações",
        type="revenue",
        pnl_section="revenue"
    ),
    
    # Cost of Revenue (COGS)
    "cogs_payment": FinancialGroup(
        id="cogs_payment",
        name="Payment Processing",
        type="cost",
        pnl_section="cogs",
        calculation_rule="payment_processing_1765"  # 17.65% da receita líquida
    ),
    "cogs_aws": FinancialGroup(
        id="cogs_aws",
        name="AWS - Web Services",
        type="cost",
        pnl_section="cogs"
    ),
    "cogs_cloudflare": FinancialGroup(
        id="cogs_cloudflare",
        name="Cloudflare",
        type="cost",
        pnl_section="cogs"
    ),
    "cogs_heroku": FinancialGroup(
        id="cogs_heroku",
        name="Heroku",
        type="cost",
        pnl_section="cogs"
    ),
    "cogs_iaphub": FinancialGroup(
        id="cogs_iaphub",
        name="IAPHUB",
        type="cost",
        pnl_section="cogs"
    ),
    "cogs_mailgun": FinancialGroup(
        id="cogs_mailgun",
        name="Mailgun",
        type="cost",
        pnl_section="cogs"
    ),
    "cogs_aws_ses": FinancialGroup(
        id="cogs_aws_ses",
        name="AWS SES",
        type="cost",
        pnl_section="cogs"
    ),
    
    # Operating Expenses - SG&A
    "opex_marketing": FinancialGroup(
        id="opex_marketing",
        name="Marketing & Growth",
        type="expense",
        pnl_section="opex"
    ),
    "opex_wages": FinancialGroup(
        id="opex_wages",
        name="Wages",
        type="expense",
        pnl_section="opex"
    ),
    "opex_tech_support": FinancialGroup(
        id="opex_tech_support",
        name="Tech Support & Services",
        type="expense",
        pnl_section="opex"
    ),
    "opex_legal": FinancialGroup(
        id="opex_legal",
        name="Legal & Accounting",
        type="expense",
        pnl_section="opex"
    ),
    "opex_office": FinancialGroup(
        id="opex_office",
        name="Office Expenses",
        type="expense",
        pnl_section="opex"
    ),
    "opex_travel": FinancialGroup(
        id="opex_travel",
        name="Travel",
        type="expense",
        pnl_section="opex"
    ),
    "opex_taxes": FinancialGroup(
        id="opex_taxes",
        name="Other Taxes",
        type="expense",
        pnl_section="opex"
    ),
}


# ============================================================================
# 33 P&L MAPPING RULES (from Business Plan Umatch)
# ============================================================================

@dataclass
class MappingRule:
    """Mapping rule for Conta Azul → P&L."""
    id: int
    financial_group: str
    cost_center: str
    supplier: str
    pnl_line: int
    type: str  # "Receita", "Custo", "Despesa"
    active: bool = True
    notes: str = ""


# Pre-configured 33 mapping rules based on Business Plan Umatch documentation
CONTA_AZUL_MAPPING_RULES: List[MappingRule] = [
    # ========== RECEITAS (Revenue) ==========
    MappingRule(1, "receita_google", "Google Play Net Revenue", "Google Brasil Pagamentos LTDA", 10, "Receita"),
    MappingRule(2, "receita_google", "Google Play Net Revenue", "Google Brasil Pagamentos Ltda", 10, "Receita"),
    MappingRule(3, "receita_apple", "App Store Net Revenue", "App Store (Apple)", 11, "Receita"),
    MappingRule(4, "receita_apple", "App Store Net Revenue", "Apple Inc", 11, "Receita"),
    MappingRule(5, "receita_rendimentos", "Rendimentos", "Conta Simples", 12, "Receita"),
    MappingRule(6, "receita_rendimentos", "Rendimentos", "Banco Inter", 12, "Receita"),
    MappingRule(7, "receita_rendimentos", "Rendimentos de Aplicações", "Conta Simples", 12, "Receita"),
    MappingRule(8, "receita_rendimentos", "Rendimentos de Aplicações", "Banco Inter", 12, "Receita"),
    
    # ========== COGS (Cost of Goods Sold) ==========
    MappingRule(9, "cogs_aws", "Web Services Expenses", "AWS", 20, "Custo"),
    MappingRule(10, "cogs_aws", "Web Services Expenses", "Amazon Web Services", 20, "Custo"),
    MappingRule(11, "cogs_cloudflare", "Web Services Expenses", "Cloudflare", 21, "Custo"),
    MappingRule(12, "cogs_heroku", "Web Services Expenses", "Heroku", 22, "Custo"),
    MappingRule(13, "cogs_iaphub", "Web Services Expenses", "IAPHUB", 23, "Custo"),
    MappingRule(14, "cogs_mailgun", "Web Services Expenses", "Mailgun", 24, "Custo"),
    MappingRule(15, "cogs_aws_ses", "Web Services Expenses", "AWS SES", 25, "Custo"),
    MappingRule(16, "cogs_aws_ses", "Web Services Expenses", "Amazon SES", 25, "Custo"),
    
    # ========== OpEx - Marketing ==========
    MappingRule(17, "opex_marketing", "Marketing & Growth Expenses", "*", 30, "Despesa", notes="Todos os fornecedores de marketing"),
    MappingRule(18, "opex_marketing", "Marketing", "*", 30, "Despesa"),
    MappingRule(19, "opex_marketing", "Publicidade", "*", 30, "Despesa"),
    
    # ========== OpEx - Wages ==========
    MappingRule(20, "opex_wages", "Wages Expenses", "*", 31, "Despesa"),
    MappingRule(21, "opex_wages", "Salários", "*", 31, "Despesa"),
    MappingRule(22, "opex_wages", "Folha de Pagamento", "*", 31, "Despesa"),
    
    # ========== OpEx - Tech Support ==========
    MappingRule(23, "opex_tech_support", "Tech Support & Services", "*", 32, "Despesa"),
    MappingRule(24, "opex_tech_support", "Suporte Técnico", "*", 32, "Despesa"),
    
    # ========== OpEx - Legal & Accounting ==========
    MappingRule(25, "opex_legal", "Legal & Accounting", "*", 33, "Despesa"),
    MappingRule(26, "opex_legal", "Contabilidade", "*", 33, "Despesa"),
    MappingRule(27, "opex_legal", "Jurídico", "*", 33, "Despesa"),
    
    # ========== OpEx - Office ==========
    MappingRule(28, "opex_office", "Office Expenses", "*", 34, "Despesa"),
    MappingRule(29, "opex_office", "Office Expenses", "GO Offices", 34, "Despesa"),
    MappingRule(30, "opex_office", "Office Expenses", "Co-Services", 34, "Despesa"),
    
    # ========== OpEx - Travel ==========
    MappingRule(31, "opex_travel", "Travel", "*", 35, "Despesa"),
    MappingRule(32, "opex_travel", "Viagens", "*", 35, "Despesa"),
    
    # ========== OpEx - Other Taxes ==========
    MappingRule(33, "opex_taxes", "Other Taxes", "*", 36, "Despesa"),
]


# ============================================================================
# MAPPING LOOKUP FUNCTIONS
# ============================================================================

def find_mapping_rule(cost_center: str, supplier: str) -> Optional[MappingRule]:
    """
    Find the best matching mapping rule for a transaction.
    
    Priority:
    1. Exact match on both cost_center and supplier
    2. Match on cost_center with wildcard (*) supplier
    3. No match
    """
    cost_center_lower = cost_center.lower().strip() if cost_center else ""
    supplier_lower = supplier.lower().strip() if supplier else ""
    
    # First pass: exact match
    for rule in CONTA_AZUL_MAPPING_RULES:
        if not rule.active:
            continue
        if rule.cost_center.lower() == cost_center_lower:
            if rule.supplier == "*" or rule.supplier.lower() == supplier_lower:
                return rule
    
    # Second pass: partial match on cost_center
    for rule in CONTA_AZUL_MAPPING_RULES:
        if not rule.active:
            continue
        if cost_center_lower in rule.cost_center.lower() or rule.cost_center.lower() in cost_center_lower:
            if rule.supplier == "*" or rule.supplier.lower() == supplier_lower:
                return rule
    
    return None


def get_financial_group(group_id: str) -> Optional[FinancialGroup]:
    """Get financial group by ID."""
    return FINANCIAL_GROUPS.get(group_id)


def classify_transaction(cost_center: str, supplier: str, amount: float) -> Dict[str, Any]:
    """
    Classify a transaction based on mapping rules.
    
    Returns:
        {
            "mapped": bool,
            "group": FinancialGroup or None,
            "rule": MappingRule or None,
            "pnl_line": int or None,
            "type": "Receita"|"Custo"|"Despesa"|None
        }
    """
    rule = find_mapping_rule(cost_center, supplier)
    
    if rule:
        group = get_financial_group(rule.financial_group)
        return {
            "mapped": True,
            "group": asdict(group) if group else None,
            "rule_id": rule.id,
            "pnl_line": rule.pnl_line,
            "type": rule.type,
            "financial_group": rule.financial_group
        }
    
    return {
        "mapped": False,
        "group": None,
        "rule_id": None,
        "pnl_line": None,
        "type": None,
        "financial_group": None
    }


# ============================================================================
# CALCULATION RULES
# ============================================================================

def calculate_gross_from_net(net_amount: float, rate: float = 0.85) -> float:
    """
    Calculate gross revenue from net.
    Receita Bruta = Receita Líquida / 0.85
    """
    if rate == 0:
        return net_amount
    return net_amount / rate


def calculate_payment_processing(net_revenue: float, rate: float = 0.1765) -> float:
    """
    Calculate payment processing cost.
    Payment Processing = 17.65% × Receita Líquida
    """
    return net_revenue * rate


# ============================================================================
# TEMPLATE GENERATION
# ============================================================================

def generate_conta_azul_plan() -> Dict[str, Any]:
    """
    Generate a complete v1.3 normalization plan for Conta Azul format.
    """
    return {
        "schema_version": "1.3",
        "needs_user_review": False,
        "confidence": 0.95,
        "summary": {
            "detected_layout": "Conta Azul - Extrato Financeiro (formato padrão)",
            "key_decisions": [
                "Date=Data de competência (DD/MM/YYYY)",
                "Amount=Valor (R$ pt-BR format)",
                "Cost Center=Centro de custo",
                "Supplier=Fornecedor/Cliente"
            ],
            "main_risks": []
        },
        "template_fingerprint": {
            "basis": {
                "normalized_columns": [
                    "data de competência",
                    "centro de custo",
                    "fornecedor/cliente",
                    "descrição",
                    "valor",
                    "tipo de operação",
                    "categoria"
                ],
                "column_count": 7,
                "delimiter": ";",
                "has_header": True
            },
            "hash": "conta_azul_extrato_v1",
            "recommended_template_name": "conta_azul_extrato_v1"
        },
        "privacy": {
            "contains_pii": False,
            "pii_fields": [],
            "notes": "Financial data only"
        },
        "csv_read": {
            "delimiter": ";",
            "delimiter_candidates": [{"delimiter": ";", "score": 0.99}],
            "encoding_hint": "utf-8",
            "has_header": True,
            "header_confidence": 0.98,
            "quote_char": '"',
            "skip_rows": 0
        },
        "input_profile": {
            "columns": CONTA_AZUL_CONFIG["expected_columns"],
            "column_count": 7,
            "language_hint": "pt-BR"
        },
        "mapping": {
            "date": {
                "source": "Data de competência",
                "method": "parse_date",
                "formats": ["DD/MM/YYYY"],
                "timezone_strategy": "ignore_time_keep_date"
            },
            "description": {
                "source": "Descrição",
                "method": "direct"
            },
            "amount": {
                "source": "Valor",
                "method": "parse_money_ptbr",
                "decimal": ",",
                "thousand": ".",
                "negative_style": "leading_minus"
            },
            "operation_type": {
                "source": "Tipo de operação",
                "method": "direct"
            },
            "cost_center": {
                "source": "Centro de custo",
                "method": "direct"
            },
            "supplier": {
                "source": "Fornecedor/Cliente",
                "method": "direct"
            },
            "category": {
                "source": "Categoria",
                "method": "direct"
            },
            "currency": {
                "method": "set_constant",
                "value": "BRL"
            },
            "raw_passthrough": True
        },
        "transform_plan": [
            {"op": "read_csv", "args": {"delimiter": ";", "has_header": True}},
            {"op": "trim", "source": "*", "target": "*", "params": {}},
            {"op": "parse_date", "source": "Data de competência", "target": "date", "params": {"formats": ["DD/MM/YYYY"]}},
            {"op": "parse_money_ptbr", "source": "Valor", "target": "amount", "params": {"decimal": ",", "thousand": "."}},
            {"op": "derive_from_amount_sign", "source": "amount", "target": "operation_type", "params": {}},
            {"op": "set_raw_passthrough", "args": {"enabled": True}}
        ],
        "quality_checks": {
            "required_fields": ["date", "description", "amount"],
            "thresholds": {
                "date_parse_success_rate_min": 0.95,
                "amount_parse_success_rate_min": 0.95,
                "non_empty_description_rate_min": 0.90
            },
            "validations": [
                {"type": "date_parse_success_rate", "args": {"min": 0.95}},
                {"type": "amount_parse_success_rate", "args": {"min": 0.95}}
            ]
        },
        "duplicate_detection": {
            "strategy": "hash",
            "hash_fields": ["date", "amount", "description", "cost_center", "supplier"],
            "normalization": {
                "description_normalize_accents": True,
                "description_lowercase": True,
                "trim": True,
                "collapse_whitespace": True
            }
        },
        "warnings": []
    }


def get_mapping_rules_summary() -> Dict[str, Any]:
    """Get summary of all mapping rules."""
    by_type = {"Receita": [], "Custo": [], "Despesa": []}
    
    for rule in CONTA_AZUL_MAPPING_RULES:
        if rule.active:
            by_type[rule.type].append({
                "id": rule.id,
                "cost_center": rule.cost_center,
                "supplier": rule.supplier,
                "group": rule.financial_group
            })
    
    return {
        "total_rules": len(CONTA_AZUL_MAPPING_RULES),
        "active_rules": sum(1 for r in CONTA_AZUL_MAPPING_RULES if r.active),
        "by_type": {
            "receita": len(by_type["Receita"]),
            "custo": len(by_type["Custo"]),
            "despesa": len(by_type["Despesa"])
        },
        "rules": by_type
    }
