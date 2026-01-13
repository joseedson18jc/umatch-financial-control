import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
import io
import logging
import os
from typing import List, Dict, Any, Optional
from collections import defaultdict
import unicodedata
from models import MappingItem, PnLItem, PnLResponse, DashboardData

# Configure logging for financial calculations
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_upload(file_content: bytes) -> pd.DataFrame:
    """
    Process the uploaded CSV file from Conta Azul.
    """
    # Try different encodings and separators
    df = None
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    separators = [',', ';', '\t']
    last_error = None
    
    for encoding in encodings:
        for sep in separators:
            try:
                # Try strict parsing first
                df = pd.read_csv(io.BytesIO(file_content), encoding=encoding, sep=sep)
                
                # Check if it has the critical column 'Data de competência'
                if 'Data de competência' in df.columns:
                    break
                else:
                    df = None # Not the right separator
            except Exception:
                continue
        
        if df is not None:
            break
            
        # If strict parsing failed for this encoding, try with on_bad_lines='skip' as fallback
        for sep in separators:
            try:
                print(f"⚠️ Strict parsing failed. Retrying with on_bad_lines='skip', encoding={encoding}, sep='{sep}'")
                df = pd.read_csv(io.BytesIO(file_content), encoding=encoding, sep=sep, on_bad_lines='skip', engine='python')
                if 'Data de competência' in df.columns:
                    break
                else:
                    df = None
            except Exception as e:
                last_error = e
                continue
        
        if df is not None:
            break
    
    if df is None:
        if last_error:
            raise ValueError(f"Error reading CSV file. Please ensure it's a valid CSV. Details: {last_error}")
        else:
            raise ValueError("Error reading CSV file. Could not detect valid format (encoding/separator).")

    # Normalize column names - strip whitespace
    df.columns = [c.strip() for c in df.columns]
    
    # Column name mapping for flexibility (handle different Conta Azul export formats)
    column_aliases = {
        'Data de competência': ['Data de competência', 'Data de Competência', 'Data Competência', 'data_competencia', 'Data'],
        'Valor (R$)': ['Valor (R$)', 'Valor', 'Valor R$', 'valor', 'VALOR'],
        'Tipo': [
            'Tipo', 'tipo',
            'Entrada/Saída', 'Entrada/Saida',
            'Tipo (Entrada/Saída)', 'Tipo (Entrada/Saida)',
            'Tipo de movimentação', 'Tipo de Movimentação',
            'Tipo da operação', 'Tipo da operacao', 'Tipo da Operação', 'Tipo da Operacao',
            'Tipo da operação ', 'Tipo da operacao ',
            'Natureza', 'natureza'
        ],
        'Centro de Custo 1': ['Centro de Custo 1', 'Centro de Custo', 'CentroCusto', 'centro_custo', 'Centro de custo 1'],
        'Nome do fornecedor/cliente': ['Nome do fornecedor/cliente', 'Fornecedor/Cliente', 'Nome Fornecedor', 'fornecedor_cliente', 'Fornecedor', 'Cliente']
    }
    
    # Try to find and rename columns
    for target_col, aliases in column_aliases.items():
        if target_col not in df.columns:
            for alias in aliases:
                if alias in df.columns:
                    df.rename(columns={alias: target_col}, inplace=True)
                    print(f"✅ Mapped column '{alias}' -> '{target_col}'")
                    break
    
    # Print available columns for debugging
    print(f"📋 Available columns after normalization: {list(df.columns)}")

    # Basic validation
    required_cols = ['Data de competência', 'Valor (R$)', 'Centro de Custo 1', 'Nome do fornecedor/cliente']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        available = ', '.join(df.columns[:10])  # Show first 10 columns
        raise ValueError(f"Missing required columns: {missing_cols}. Available columns: {available}...")

    # Data cleaning
    
    # Robust date parsing
    def parse_dates(date_str):
        if pd.isna(date_str): return pd.NaT
        date_str = str(date_str).strip()
        formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
        return pd.NaT

    df['Data de competência'] = df['Data de competência'].apply(parse_dates)
    
    def normalize_text(s: Any) -> str:
        if pd.isna(s):
            return ""
        s = str(s).strip().lower()
        s = unicodedata.normalize("NFKD", s)
        return "".join(ch for ch in s if not unicodedata.combining(ch))
    
    def converter_valor_br(valor_str: Any) -> float:
        if pd.isna(valor_str) or str(valor_str).strip() == "":
            return 0.0

        s = str(valor_str).replace('R$', '').strip()

        negative = False
        # (1.234,56) accounting negative
        if s.startswith('(') and s.endswith(')'):
            negative = True
            s = s[1:-1].strip()

        # 1.234,56- trailing minus
        if s.endswith('-'):
            negative = True
            s = s[:-1].strip()

        # Remove spaces
        s = s.replace(' ', '')

        # Brazilian vs US separators
        if ',' in s and '.' in s:
            if s.rfind(',') > s.rfind('.'):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif ',' in s:
            s = s.replace(',', '.')

        try:
            v = float(s)
            return -v if negative else v
        except ValueError:
            return 0.0

    df['Valor_Num'] = df['Valor (R$)'].apply(converter_valor_br)

    if 'Tipo' in df.columns:
        tipo = df['Tipo'].apply(normalize_text)

        is_saida = (
            tipo.str.contains('saida') |
            tipo.str.contains('debito') |
            tipo.str.contains('despesa') |
            tipo.str.contains('pagamento')
        )
        # Entrada/Credito/Receita -> positive
        sign = np.where(is_saida, -1.0, 1.0)

        # IMPORTANT: ignore any embedded minus in the numeric string,
        # because Tipo is the source of truth.
        df['Valor_Num'] = df['Valor_Num'].abs() * sign
        
        # Validation Log
        logger.info("Tipo normalization applied.")
        logger.info(f"Tipo counts: {tipo.value_counts().to_dict()}")
        logger.info(f"Sum Valor_Num (signed): {df['Valor_Num'].sum():.2f}")
        logger.info(f"Sum abs Valor_Num: {df['Valor_Num'].abs().sum():.2f}")
    else:
        logger.warning("CSV has no Tipo/Entrada-Saída column; using sign embedded in Valor (R$).")
    df['Mes_Competencia'] = df['Data de competência'].dt.to_period('M')
    
    # Normalize text columns for mapping
    if 'Centro de Custo 1' in df.columns:
        df['Centro de Custo 1'] = df['Centro de Custo 1'].astype(str).str.strip()
    if 'Nome do fornecedor/cliente' in df.columns:
        df['Nome do fornecedor/cliente'] = df['Nome do fornecedor/cliente'].astype(str).str.strip()
    
    return df

def get_initial_mappings() -> List[MappingItem]:
    """Get initial/default mappings.

    These mappings are designed to match common Conta Azul exports. We keep
    a few legacy aliases (e.g. 'Receita Google') so older workbooks still map.
    """

    def mi(
        grupo: str,
        centro_custo: str,
        fornecedor: str,
        linha_pl: int,
        tipo: str,
        obs: str = "",
    ) -> MappingItem:
        return MappingItem(
            grupo_financeiro=grupo,
            centro_custo=centro_custo,
            fornecedor_cliente=fornecedor,
            linha_pl=str(linha_pl),
            tipo=tipo,
            ativo="Sim",
            observacoes=obs,
        )

    mappings: List[MappingItem] = [
        # =====================
        # RECEITAS
        # =====================
        mi("Receita Google", "Google Play Net Revenue", "Diversos", 25, "Receita", "Google Play (net)"),
        mi("Receita Google", "Receita Google", "Diversos", 25, "Receita", "Alias legado"),
        mi("Receita Apple", "App Store Net Revenue", "Diversos", 33, "Receita", "App Store (net)"),
        mi("Receita Apple", "Receita Apple", "Diversos", 33, "Receita", "Alias legado"),

        # Refunds / chargebacks (contra-receita)
        mi("Devoluções e Estornos", "Devoluções e Estornos", "Diversos", 34, "Receita", "Refunds & Chargebacks"),

        # Rendimentos
        mi("Rendimentos", "Rendimentos de Aplicações", "CONTA SIMPLES", 38, "Receita", "Rendimentos CDI - Conta Simples"),
        mi("Rendimentos", "Rendimentos de Aplicações", "BANCO INTER", 38, "Receita", "Rendimentos - Banco Inter"),
        mi("Rendimentos", "Rendimentos de Aplicações", "Diversos", 38, "Receita", "Outros rendimentos"),

        # =====================
        # COGS (Web Services)
        # =====================
        mi("COGS", "Web Services Expenses", "AWS", 43, "Custo", "Amazon Web Services"),
        mi("COGS", "Web Services Expenses", "Cloudflare", 44, "Custo", "Cloudflare"),
        mi("COGS", "Web Services Expenses", "Heroku", 45, "Custo", "Heroku"),
        mi("COGS", "Web Services Expenses", "IAPHUB", 46, "Custo", "IAPHUB"),
        mi("COGS", "Web Services Expenses", "MailGun", 47, "Custo", "MailGun"),
        mi("COGS", "Web Services Expenses", "AWS SES", 48, "Custo", "AWS SES"),
        mi("COGS", "Web Services Expenses", "Diversos", 49, "Custo", "Outros Web Services"),

        # =====================
        # SG&A
        # =====================
        mi("SG&A", "Marketing & Growth Expenses", "Diversos", 56, "Despesa", "Marketing"),
        mi("SG&A", "Wages Expenses", "Diversos", 62, "Despesa", "Salários e Pró-labore"),

        mi("SG&A", "Tech Support & Services", "Adobe", 68, "Despesa", "Adobe Creative Cloud"),
        mi("SG&A", "Tech Support & Services", "Canva", 68, "Despesa", "Canva"),
        mi("SG&A", "Tech Support & Services", "ClickSign", 68, "Despesa", "ClickSign"),
        mi("SG&A", "Tech Support & Services", "COMPANYHERO", 68, "Despesa", "CompanyHero"),
        mi("SG&A", "Tech Support & Services", "Diversos", 65, "Despesa", "Tech Support (outros)"),

        # =====================
        # OUTRAS DESPESAS / TAXAS
        # =====================
        mi("Outras Despesas", "Legal & Accounting Expenses", "BHUB", 90, "Despesa", "BPO Financeiro"),
        mi("Outras Despesas", "Legal & Accounting Expenses", "WOLFF", 90, "Despesa", "Honorários Advocatícios"),
        mi("Outras Despesas", "Legal & Accounting Expenses", "Diversos", 90, "Despesa", "Legal & Accounting (geral)"),

        mi("Outras Despesas", "Office Expenses", "GO OFFICES", 90, "Despesa", "Aluguel"),
        mi("Outras Despesas", "Office Expenses", "Diversos", 90, "Despesa", "Office (geral)"),

        mi("Outras Despesas", "Travel", "Diversos", 90, "Despesa", "Viagens"),
        mi("Outras Despesas", "Other Taxes", "IMPOSTOS", 90, "Despesa", "Impostos e Tributos"),
        mi("Outras Despesas", "Payroll Tax - Brazil", "IMPOSTOS", 90, "Despesa", "Impostos sobre Folha"),
        mi("Outras Despesas", "Advisory & Prof. Services Expenses", "Diversos", 90, "Despesa", "Serviços profissionais"),
        mi("Outras Despesas", "Operating Expenses", "Diversos", 90, "Despesa", "Despesas operacionais"),
        mi("Outras Despesas", "Other Expenses", "Diversos", 90, "Despesa", "Outras despesas"),
        mi("Outras Despesas", "Identificar", "Diversos", 90, "Despesa", "Centro de custo não classificado"),
    ]

    return mappings
def normalize_text_helper(s: Any) -> str:
    # Helper outside process_upload for use in calculate_pnl
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))

def prepare_mappings(mappings: List[MappingItem]):
    from collections import defaultdict
    
    # Use defaultdict(list) for specific mappings to handle multiple patterns for same CC
    specific_by_cc = defaultdict(list)
    generic_by_cc = {}

    for m in mappings:
        cc = normalize_text_helper(m.centro_custo)
        supp = normalize_text_helper(m.fornecedor_cliente)

        if supp and supp != "diversos":
            # Specific mapping
            specific_by_cc[cc].append(m)
        else:
            # Generic mapping (fallback)
            generic_by_cc[cc] = m

    # Sort specific mappings by supplier length desc (Longest match first)
    for cc, m_list in specific_by_cc.items():
        m_list.sort(key=lambda x: len(normalize_text_helper(x.fornecedor_cliente)), reverse=True)

    return specific_by_cc, generic_by_cc

# -----------------------------------------------------------------------------
# Diagnostics and suggestions
# -----------------------------------------------------------------------------

def get_unmapped_diagnostics(
    df: pd.DataFrame,
    mappings: List[MappingItem],
    month: Optional[str] = None,
) -> Dict[str, Any]:
    """Compute statistics for unmapped transactions.

    Args:
        df: Normalized DataFrame returned by process_upload.
        mappings: Current mapping list.
        month: Optional month filter (YYYY-MM). If provided, only rows for that month are considered.

    Returns:
        Dictionary with total_unmapped_count, total_unmapped_amount (abs sum),
        unmapped_pct (by count), and breakdowns by cost center, category, supplier.
    """
    if df is None or df.empty:
        return {
            "total_unmapped_count": 0,
            "total_unmapped_amount": 0.0,
            "unmapped_pct": 0.0,
            "by_cost_center": [],
            "by_category": [],
            "by_supplier": [],
        }

    # Build mapping indices similar to calculate_pnl
    active_mappings = [m for m in mappings if str(getattr(m, "ativo", "Sim")).strip().lower() == "sim"]
    specific_by_cc: Dict[str, List[str]] = defaultdict(list)
    generic_by_cc: Dict[str, None | MappingItem] = {}
    for m in active_mappings:
        cc_norm = normalize_text_helper(m.centro_custo)
        supp_norm = normalize_text_helper(m.fornecedor_cliente)
        if supp_norm and supp_norm not in {"diversos", "nan"}:
            specific_by_cc[cc_norm].append(supp_norm)
        else:
            generic_by_cc[cc_norm] = m
    for cc_norm, lst in specific_by_cc.items():
        lst.sort(key=len, reverse=True)

    # Filter by month if provided
    filtered_df = df
    if month:
        try:
            if '-' in str(month):
                filtered_df = df[df['Mes_Competencia'].astype(str) == month]
            else:
                filtered_df = df[df['Mes_Competencia'] == month]
        except Exception:
            pass

    total_count = 0
    total_unmapped_count = 0
    total_unmapped_amount = 0.0

    # Aggregation dictionaries
    by_cc: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "amount": 0.0})
    by_cat: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "amount": 0.0})
    by_supp: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "amount": 0.0})

    for _, row in filtered_df.iterrows():
        total_count += 1
        cc = row.get('Centro de Custo 1')
        if pd.isna(cc) or str(cc).strip() == '':
            cc = row.get('Categoria 1') or row.get('Categoria')
        cc_norm = normalize_text_helper(cc)

        supplier = row.get('Nome do fornecedor/cliente')
        supplier = '' if pd.isna(supplier) else str(supplier)
        supplier_norm = normalize_text_helper(supplier)

        desc = row.get('Descrição', '')
        desc = '' if pd.isna(desc) else str(desc)
        blob_norm = normalize_text_helper(f"{supplier} {desc}")

        # Determine if mapped
        matched = False
        # Specific match
        for token in specific_by_cc.get(cc_norm, []):
            if token and token in blob_norm:
                matched = True
                break
        # Generic match
        if not matched and cc_norm in generic_by_cc:
            matched = True
        # Category fallback generic
        if not matched:
            cat = row.get('Categoria 1') or row.get('Categoria')
            cat_norm = normalize_text_helper(cat)
            if cat_norm in generic_by_cc:
                matched = True
        if not matched:
            # Unmapped
            total_unmapped_count += 1
            val = row.get('Valor_Num', 0.0)
            try:
                val = float(val)
            except Exception:
                val = 0.0
            total_unmapped_amount += abs(val)
            cc_key = str(cc).strip() if pd.notna(cc) else ''
            cat_key = str(row.get('Categoria 1') or row.get('Categoria') or '')
            supp_key = str(supplier).strip()
            by_cc[cc_key]['count'] += 1
            by_cc[cc_key]['amount'] += abs(val)
            by_cat[cat_key]['count'] += 1
            by_cat[cat_key]['amount'] += abs(val)
            by_supp[supp_key]['count'] += 1
            by_supp[supp_key]['amount'] += abs(val)

    # Convert breakdown to sorted lists
    def to_sorted_list(d: Dict[str, Dict[str, float]]):
        items = []
        for name, stats in d.items():
            items.append({"name": name, "count": int(stats['count']), "amount": round(stats['amount'], 2)})
        return sorted(items, key=lambda x: x['amount'], reverse=True)

    unmapped_pct = (total_unmapped_count / total_count) if total_count else 0.0
    return {
        "total_unmapped_count": total_unmapped_count,
        "total_unmapped_amount": round(total_unmapped_amount, 2),
        "unmapped_pct": round(unmapped_pct, 4),
        "by_cost_center": to_sorted_list(by_cc),
        "by_category": to_sorted_list(by_cat),
        "by_supplier": to_sorted_list(by_supp),
    }

def suggest_mappings(df: pd.DataFrame, mappings: List[MappingItem]) -> List[MappingItem]:
    """Generate heuristic mapping suggestions for unmapped supplier/cost center combinations.

    For each transaction that isn't covered by an existing specific mapping, suggest
    creating a new MappingItem using the generic mapping for the same cost center
    (if available). This ensures more granularity without reclassifying to a new line.

    Args:
        df: Normalized dataframe from process_upload.
        mappings: Current mappings.

    Returns:
        A list of proposed MappingItem objects (not yet persisted).
    """
    suggestions: Dict[Tuple[str, str], MappingItem] = {}
    # Build mapping lookup for existing centro_custo + fornecedor pairs
    existing_pairs = set()
    cc_to_generic = {}
    for m in mappings:
        cc_norm = normalize_text_helper(m.centro_custo)
        supp_norm = normalize_text_helper(m.fornecedor_cliente)
        existing_pairs.add((cc_norm, supp_norm))
        # Generic mapping (fornecedor = Diversos or empty) to use as template
        if not supp_norm or supp_norm == 'diversos' or supp_norm == 'nan':
            cc_to_generic[cc_norm] = m

    # Iterate over df
    for _, row in df.iterrows():
        cc = row.get('Centro de Custo 1')
        if pd.isna(cc) or str(cc).strip() == '':
            cc = row.get('Categoria 1') or row.get('Categoria')
        cc_norm = normalize_text_helper(cc)
        supplier = row.get('Nome do fornecedor/cliente')
        supplier = '' if pd.isna(supplier) else str(supplier)
        supp_norm = normalize_text_helper(supplier)
        if (cc_norm, supp_norm) in existing_pairs:
            continue
        # Must have generic mapping to base
        base = cc_to_generic.get(cc_norm)
        if not base:
            continue
        # Create suggestion
        new_mapping = MappingItem(
            grupo_financeiro=base.grupo_financeiro,
            centro_custo=base.centro_custo,
            fornecedor_cliente=supplier.strip(),
            linha_pl=base.linha_pl,
            tipo=base.tipo,
            ativo="Sim",
            observacoes=f"Sugestão automática para fornecedor '{supplier.strip()}'"
        )
        suggestions[(cc_norm, supp_norm)] = new_mapping

    return list(suggestions.values())

def calculate_pnl(
    df: pd.DataFrame,
    mappings: List[MappingItem],
    overrides: Dict[str, Dict[str, float]] = None,
    start_date: str = None,
    end_date: str = None
) -> PnLResponse:
    """Calculate P&L based on dataframe and mappings.

    Assumes `process_upload` already normalized signs using the 'Tipo' column:
      - Receita / Crédito / Entrada  -> positive
      - Despesa / Débito / Saída     -> negative

    Derived logic:
      - We treat app revenues as *net receipts* (after store commission).
      - We derive *gross* app revenue by dividing by STORE_NET_RATE (default 0.85).
      - Store fee (payment processing) is the difference between gross and net.
    """
    if overrides is None:
        overrides = {}

    if df is None or df.empty:
        return PnLResponse(headers=[], rows=[])

    filtered_df = df.copy()

    # Date filter (defensive)
    if start_date:
        start = pd.to_datetime(start_date, errors="coerce")
        if pd.notna(start):
            filtered_df = filtered_df[filtered_df['Data de competência'] >= start]
    if end_date:
        end = pd.to_datetime(end_date, errors="coerce")
        if pd.notna(end):
            filtered_df = filtered_df[filtered_df['Data de competência'] <= end]

    if filtered_df.empty:
        return PnLResponse(headers=[], rows=[])

    # Months
    months = sorted(filtered_df['Mes_Competencia'].dropna().unique())
    month_strs = [str(m) for m in months]
    if not month_strs:
        return PnLResponse(headers=[], rows=[])

    # Active mappings only
    active_mappings = [m for m in mappings if str(getattr(m, "ativo", "Sim")).strip().lower() == "sim"]

    # Build fast mapping indices (cc_norm -> specific supplier patterns, plus generic)
    specific_by_cc: Dict[str, List[tuple[str, int]]] = defaultdict(list)
    generic_by_cc: Dict[str, int] = {}
    base_lines: set[int] = set()

    for m_item in active_mappings:
        try:
            ln = int(m_item.linha_pl)
        except Exception:
            continue

        base_lines.add(ln)

        cc_norm = normalize_text_helper(m_item.centro_custo)
        supp_norm = normalize_text_helper(m_item.fornecedor_cliente)

        if supp_norm and supp_norm not in {"diversos", "nan"}:
            specific_by_cc[cc_norm].append((supp_norm, ln))
        else:
            generic_by_cc[cc_norm] = ln

    # Longest supplier token first
    for cc_norm, lst in specific_by_cc.items():
        lst.sort(key=lambda t: len(t[0]), reverse=True)

    # Accumulator: line -> month -> value
    line_values: Dict[int, Dict[str, float]] = defaultdict(lambda: {m: 0.0 for m in month_strs})
    unmapped_count = 0

    for _, row in filtered_df.iterrows():
        cc = row.get('Centro de Custo 1')
        if pd.isna(cc) or str(cc).strip() == '':
            cc = row.get('Categoria 1') or row.get('Categoria')
        cc_norm = normalize_text_helper(cc)

        supplier = row.get('Nome do fornecedor/cliente')
        supplier = '' if pd.isna(supplier) else str(supplier)

        desc = row.get('Descrição', '')
        desc = '' if pd.isna(desc) else str(desc)

        blob_norm = normalize_text_helper(f"{supplier} {desc}")

        month = str(row.get('Mes_Competencia', ''))
        if month not in month_strs:
            continue

        try:
            value = float(row.get('Valor_Num', 0.0))
        except Exception:
            continue

        line_num = None

        # Specific rules
        for supp_norm, ln in specific_by_cc.get(cc_norm, []):
            if supp_norm and supp_norm in blob_norm:
                line_num = ln
                break

        # Generic fallback (same cost center)
        if line_num is None:
            line_num = generic_by_cc.get(cc_norm)

        # Category fallback
        if line_num is None:
            cat = row.get('Categoria 1') or row.get('Categoria')
            cat_norm = normalize_text_helper(cat)
            line_num = generic_by_cc.get(cat_norm)

        if line_num is None:
            unmapped_count += 1
            continue

        line_values[line_num][month] += value

    if unmapped_count:
        logger.warning("%s transactions could not be mapped", unmapped_count)

    # Apply overrides to base lines first
    derived_overrides: Dict[int, Dict[str, float]] = defaultdict(dict)
    for line_str, month_vals in overrides.items():
        try:
            ln = int(line_str)
        except Exception:
            continue

        for m_str, v in (month_vals or {}).items():
            if m_str not in month_strs:
                continue
            try:
                v = float(v)
            except Exception:
                continue

            if ln in base_lines:
                line_values[ln][m_str] = v
            else:
                derived_overrides[ln][m_str] = v

    # Derived lines
    try:
        net_rate = float(os.getenv("STORE_NET_RATE", "0.85"))
    except Exception:
        net_rate = 0.85
    net_rate = min(max(net_rate, 0.01), 1.0)

    cogs_lines = [43, 44, 45, 46, 47, 48, 49]

    for m_str in month_strs:
        google_net = line_values[25][m_str]
        apple_net = line_values[33][m_str]
        refunds_adj = line_values[34][m_str]
        invest_income = line_values[38][m_str]

        net_receipts_apps = google_net + apple_net + refunds_adj
        gross_apps_revenue = net_receipts_apps / net_rate
        store_fee = gross_apps_revenue - net_receipts_apps

        total_revenue_gross = gross_apps_revenue + invest_income

        cogs_total_signed = sum(line_values[ln][m_str] for ln in cogs_lines)

        # Gross profit
        gross_profit = total_revenue_gross + cogs_total_signed - store_fee

        # Operating expenses
        tech_total = line_values[65][m_str] + line_values[68][m_str]
        sga_total_signed = line_values[56][m_str] + line_values[62][m_str] + tech_total
        other_total_signed = line_values[90][m_str]
        opex_total_signed = sga_total_signed + other_total_signed

        ebitda = gross_profit + opex_total_signed

        # Store derived (signs: fees are expenses -> negative)
        line_values[100][m_str] = total_revenue_gross
        line_values[101][m_str] = net_receipts_apps
        line_values[102][m_str] = -store_fee
        line_values[103][m_str] = cogs_total_signed
        line_values[104][m_str] = gross_profit
        line_values[69][m_str] = tech_total
        line_values[105][m_str] = sga_total_signed
        line_values[115][m_str] = opex_total_signed
        line_values[106][m_str] = ebitda
        line_values[111][m_str] = ebitda

        if abs(total_revenue_gross) > 1e-9:
            line_values[9002][m_str] = gross_profit / total_revenue_gross
            line_values[9001][m_str] = ebitda / total_revenue_gross
        else:
            line_values[9002][m_str] = 0.0
            line_values[9001][m_str] = 0.0

    # Apply overrides to derived lines last
    for ln, mv in derived_overrides.items():
        for m_str, v in mv.items():
            line_values[ln][m_str] = v

    # Build rows. IMPORTANT: keep leaf line_numbers equal to mapping lines for drilldown.
    rows: List[PnLItem] = []

    def add_row(line_number: int, description: str, values: Dict[str, float], *, is_total=False, is_header=False):
        rows.append(PnLItem(
            line_number=line_number,
            description=description,
            values={m: float(values.get(m, 0.0)) for m in month_strs},
            is_total=is_total,
            is_header=is_header,
        ))

    # Revenue (gross)
    add_row(1000, "RECEITA OPERACIONAL BRUTA", line_values[100], is_total=True, is_header=True)
    add_row(101, "Receita Líquida (Apps) — Net Receipts", line_values[101], is_total=True)
    add_row(25, "Google Play Net Revenue", line_values[25])
    add_row(33, "App Store Net Revenue", line_values[33])
    add_row(34, "Devoluções e Estornos", line_values[34])
    add_row(38, "Rendimentos de Aplicações", line_values[38])

    # Direct costs
    direct_costs_total = {m: line_values[102][m] + line_values[103][m] for m in month_strs}
    add_row(2000, "(-) CUSTOS DIRETOS", direct_costs_total, is_total=True, is_header=True)
    add_row(102, "(-) Payment Processing (Store Fees)", line_values[102], is_total=True)
    add_row(103, "(-) COGS — Web Services (Total)", line_values[103], is_total=True)
    for ln, label in [
        (43, "AWS"),
        (44, "Cloudflare"),
        (45, "Heroku"),
        (46, "IAPHUB"),
        (47, "MailGun"),
        (48, "AWS SES"),
        (49, "Web Services — Outros"),
    ]:
        add_row(ln, label, line_values[ln])

    add_row(104, "(=) LUCRO BRUTO", line_values[104], is_total=True)

    # Operating expenses
    add_row(3000, "(-) DESPESAS OPERACIONAIS", line_values[115], is_total=True, is_header=True)
    add_row(56, "Marketing", line_values[56])
    add_row(62, "Wages", line_values[62])
    add_row(69, "Tech Support & Services (Total)", line_values[69], is_total=True)
    add_row(68, "Tech Support (Fornecedores)", line_values[68])
    add_row(65, "Tech Support (Diversos)", line_values[65])
    add_row(90, "Outras Despesas", line_values[90])

    add_row(106, "(=) EBITDA", line_values[106], is_total=True)
    add_row(9002, "Margem Bruta (%)", line_values[9002], is_total=True)
    add_row(9001, "Margem EBITDA (%)", line_values[9001], is_total=True)
    add_row(111, "RESULTADO LÍQUIDO", line_values[111], is_total=True, is_header=True)

    return PnLResponse(headers=month_strs, rows=rows)
def get_dashboard_data(df: pd.DataFrame, mappings: List[MappingItem], overrides: Dict[str, Dict[str, float]] = None) -> DashboardData:
    """Generate dashboard KPIs and chart-ready series from the current P&L.

    This version uses the new P&L line numbering scheme:
      - 1000: Gross Revenue (Receita Operacional Bruta)
      - 104: Gross Profit
      - 106: EBITDA (and Net Result)
      - 25: Google Play Net Revenue
      - 33: App Store Net Revenue
      - 111: Net Result (duplicate of EBITDA)
      - 2000: Direct Costs total
      - 3000: Operating Expenses total
    """
    if df is None:
        return DashboardData(kpis={}, monthly_data=[], cost_structure={})

    pnl = calculate_pnl(df, mappings, overrides)
    if not pnl.headers:
        return DashboardData(kpis={}, monthly_data=[], cost_structure={})

    # Map PnL items by line number
    items_by_line: Dict[int, PnLItem] = {item.line_number: item for item in pnl.rows}

    def get_val(line_number: int, month: str) -> float:
        item = items_by_line.get(line_number)
        if not item:
            return 0.0
        return float(item.values.get(month, 0.0) or 0.0)

    months = pnl.headers
    # Determine latest month with non-zero revenue
    latest_month = months[-1]
    for m in reversed(months):
        if abs(get_val(1000, m)) > 1e-6:
            latest_month = m
            break

    # Aggregate KPIs across all months (YTD)
    total_revenue = sum(get_val(1000, m) for m in months)
    total_gross_profit = sum(get_val(104, m) for m in months)
    total_ebitda = sum(get_val(106, m) for m in months)
    total_google = sum(get_val(25, m) for m in months)
    total_apple = sum(get_val(33, m) for m in months)
    total_net = sum(get_val(111, m) for m in months)

    gross_margin = (total_gross_profit / total_revenue) if abs(total_revenue) > 1e-9 else 0.0
    ebitda_margin = (total_ebitda / total_revenue) if abs(total_revenue) > 1e-9 else 0.0

    kpis = {
        "total_revenue": round(total_revenue, 2),
        "gross_profit": round(total_gross_profit, 2),
        "gross_margin": round(gross_margin, 4),
        "ebitda": round(total_ebitda, 2),
        "ebitda_margin": round(ebitda_margin, 4),
        "net_result": round(total_net, 2),
        "google_revenue": round(total_google, 2),
        "apple_revenue": round(total_apple, 2),
    }

    monthly_data: List[Dict[str, Any]] = []
    for m in months:
        month_revenue = get_val(1000, m)
        month_ebitda = get_val(106, m)
        month_costs = abs(get_val(2000, m))
        month_expenses = abs(get_val(3000, m))
        monthly_data.append({
            "month": m,
            "revenue": round(month_revenue, 2),
            "ebitda": round(month_ebitda, 2),
            "costs": round(month_costs, 2),
            "expenses": round(month_expenses, 2),
        })

    # Cost structure for latest month
    cost_structure = {
        "payment_processing": abs(get_val(102, latest_month)),
        "cogs": abs(get_val(103, latest_month)),
        "marketing": abs(get_val(56, latest_month)),
        "wages": abs(get_val(62, latest_month)),
        "tech": abs(get_val(69, latest_month)),
        "other": abs(get_val(90, latest_month)),
    }

    return DashboardData(kpis=kpis, monthly_data=monthly_data, cost_structure=cost_structure)

def calculate_forecast(df: pd.DataFrame, mappings: List[MappingItem], overrides: Dict[str, Dict[str, float]] = None, months_ahead: int = 3) -> Dict[str, Any]:
    """
    Predict future financial metrics (Revenue, EBITDA) using Linear Regression.
    """
    if df is None:
        return {"forecast": []}

    # Get historical data
    pnl = calculate_pnl(df, mappings, overrides)
    
    if not pnl.headers:
        return {"forecast": []}
        
    # Prepare data for regression
    # X = Month Index (0, 1, 2...), Y = Value
    
    # We need to parse month strings 'YYYY-MM' to ordinal or just index
    months_str = pnl.headers
    
    # Helper to get line values
    def get_line_series(line_number):
        series = []
        for m in months_str:
            val = 0.0
            for row in pnl.rows:
                if row.line_number == line_number:
                    val = row.values.get(m, 0.0)
                    break
            series.append(val)
        return series

    # Use new line numbers for revenue (1000) and EBITDA (106)
    revenue_series = get_line_series(1000)
    ebitda_series = get_line_series(106)
    
    # Ensure sufficient data points (at least 3 months for a trend)
    if len(months_str) < 3:
        return {"forecast": [], "warning": "Not enough data for reliable forecast (need 3+ months)"}

    X = np.arange(len(months_str)).reshape(-1, 1)
    
    # Train Models
    model_rev = LinearRegression()
    model_rev.fit(X, revenue_series)
    
    model_ebitda = LinearRegression()
    model_ebitda.fit(X, ebitda_series)
    
    # Predict Future
    last_idx = len(months_str) - 1
    future_X = np.arange(last_idx + 1, last_idx + 1 + months_ahead).reshape(-1, 1)
    
    pred_rev = model_rev.predict(future_X)
    pred_ebitda = model_ebitda.predict(future_X)
    
    # Generate future month labels
    last_month_str = months_str[-1]
    last_date = pd.Period(last_month_str, freq='M')
    
    forecast_data = []
    for i in range(months_ahead):
        next_period = last_date + (i + 1)
        forecast_data.append({
            "month": str(next_period),
            "revenue": max(0, round(float(pred_rev[i]), 2)), # No negative revenue
            "ebitda": round(float(pred_ebitda[i]), 2),
            "is_forecast": True
        })
        
    return {"forecast": forecast_data}

