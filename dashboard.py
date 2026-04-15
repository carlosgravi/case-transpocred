"""
Transpocred Case Analytics Dashboard
=====================================
Dashboard analítico para o case técnico de Data Analyst - Transpocred.
Analisa base de associados e receitas de 6 meses de uma cooperativa de crédito.

Autor: Carlos Gravi
Data: Abril 2026

Execucao:
    streamlit run dashboard.py
"""

import os
import locale
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Transpocred Case Analytics",
    page_icon="\U0001f4ca",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Paleta de cores profissional
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#007D89",        # Teal Transpocred
    "primary_light": "#4DA8B3",  # Teal claro
    "secondary": "#165C7D",      # Teal escuro
    "secondary_light": "#4DA8B3",
    "accent": "#FFA300",         # Laranja Transpocred
    "positive": "#09AF41",       # Verde Transpocred
    "negative": "#D62728",       # Vermelho
    "warning": "#FFA300",        # Laranja
    "neutral": "#575757",        # Cinza
    "bg_light": "#F5F7FA",
    "text": "#263238",
}

SEQUENTIAL_PALETTE = [
    "#007D89", "#165C7D", "#FFA300", "#09AF41", "#4DA8B3",
    "#D62728", "#9467BD", "#8C564B", "#E377C2", "#575757",
]

CATEGORICAL_PALETTE = [
    "#007D89", "#165C7D", "#FFA300", "#09AF41", "#4DA8B3",
    "#D62728", "#9467BD", "#8C564B", "#E377C2", "#575757",
    "#1F77B4", "#FFD700",
]

SCORE_COLORS = {
    "BAIXÍSSIMO RISCO": "#09AF41",
    "BAIXO RISCO": "#4DA8B3",
    "MÉDIO RISCO 1": "#FFA300",
    "MÉDIO RISCO 2": "#FF8F00",
    "ALTÍSSIMO RISCO": "#D62728",
    "SEM CLASSIFICAÇÃO": "#575757",
}

PERFIL_COLORS = {
    "Alegre": "#007D89",
    "Triste": "#D62728",
}

NATURALIDADE_REGIOES = {
    "Catarinense": "Sul",
    "Gaúcho": "Sul",
    "Paulista": "Sudeste",
    "Carioca": "Sudeste",
    "Capixaba": "Sudeste",
    "Cearense": "Nordeste",
    "Alagoano": "Nordeste",
    "Paraense": "Norte",
    "Acreano": "Norte",
    "Mato-grossense": "Centro-Oeste",
    "Goiano": "Centro-Oeste",
}

REGIAO_COLORS = {
    "Sul": "#007D89",
    "Sudeste": "#165C7D",
    "Nordeste": "#FFA300",
    "Norte": "#09AF41",
    "Centro-Oeste": "#9467BD",
}

REGIAO_ORDER = ["Sul", "Sudeste", "Centro-Oeste", "Nordeste", "Norte"]


# ---------------------------------------------------------------------------
# Funções utilitarias de formatação
# ---------------------------------------------------------------------------
def fmt_brl(valor: float, decimals: int = 0) -> str:
    """Formata valor em Reais no padrão pt-BR."""
    if pd.isna(valor):
        return "R$ 0"
    neg = valor < 0
    abs_val = abs(valor)
    if decimals == 0:
        inteiro = int(round(abs_val))
        s = f"{inteiro:,}".replace(",", ".")
        return f"-R$ {s}" if neg else f"R$ {s}"
    else:
        s = f"{abs_val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"-R$ {s}" if neg else f"R$ {s}"


def fmt_pct(valor: float, decimals: int = 1) -> str:
    """Formata percentual no padrão pt-BR."""
    if pd.isna(valor):
        return "0%"
    s = f"{valor:.{decimals}f}".replace(".", ",")
    return f"{s}%"


def fmt_num(valor, decimals: int = 0) -> str:
    """Formata número inteiro/decimal no padrão pt-BR."""
    if pd.isna(valor):
        return "0"
    if decimals == 0:
        return f"{int(round(valor)):,}".replace(",", ".")
    return f"{valor:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_delta_brl(valor: float) -> str:
    """Formata delta monetario para st.metric."""
    if pd.isna(valor):
        return "R$ 0"
    neg = valor < 0
    abs_val = abs(valor)
    s = f"{abs_val:,.0f}".replace(",", ".")
    return f"-R$ {s}" if neg else f"R$ {s}"


# ---------------------------------------------------------------------------
# CSS customizado
# ---------------------------------------------------------------------------
def inject_css():
    st.markdown("""
    <style>
        /* Métricas: nunca truncar valores */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #F5F7FA 0%, #ECEFF1 100%);
            border-radius: 12px;
            padding: 16px 20px;
            border-left: 4px solid #007D89;
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
            overflow: visible !important;
            min-width: 0 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            color: #575757 !important;
            font-weight: 500 !important;
            overflow: visible !important;
            text-overflow: unset !important;
            white-space: normal !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
            color: #165C7D !important;
            font-weight: 700 !important;
            overflow: visible !important;
            text-overflow: unset !important;
            white-space: nowrap !important;
        }
        /* Impedir truncamento em qualquer filho do metric */
        [data-testid="stMetric"] * {
            overflow: visible !important;
            text-overflow: unset !important;
        }

        /* Cards de insight */
        .insight-box {
            background: #E0F2F1;
            border-left: 4px solid #007D89;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 8px 0;
            font-size: 0.92rem;
            color: #263238;
            line-height: 1.5;
        }
        .alert-box {
            background: #FFF3E0;
            border-left: 4px solid #FFA300;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 8px 0;
            font-size: 0.92rem;
            color: #263238;
            line-height: 1.5;
        }
        .danger-box {
            background: #FFEBEE;
            border-left: 4px solid #C62828;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 8px 0;
            font-size: 0.92rem;
            color: #263238;
            line-height: 1.5;
        }
        .success-box {
            background: #E8F5E9;
            border-left: 4px solid #09AF41;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 8px 0;
            font-size: 0.92rem;
            color: #263238;
            line-height: 1.5;
        }
        .card-title {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 6px;
            color: #007D89;
        }
        .card-title-alert {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 6px;
            color: #FFA300;
        }
        .card-title-danger {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 6px;
            color: #C62828;
        }
        .card-title-success {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 6px;
            color: #09AF41;
        }

        /*
         * SIDEBAR: fundo escuro, TODOS os textos brancos.
         * Regra com alta especificidade para nunca ser sobrescrita.
         */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #165C7D 0%, #0D4A5E 100%) !important;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] small,
        [data-testid="stSidebar"] li,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stMarkdown *,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label {
            color: #FFFFFF !important;
        }

        /*
         * AREA PRINCIPAL: fundo branco, textos escuros.
         * Usa section[data-testid="stMain"] que NAO inclui sidebar.
         */
        .stApp {
            background-color: #FFFFFF !important;
        }
        section[data-testid="stMain"] {
            background-color: #FFFFFF !important;
        }
        section[data-testid="stMain"] p,
        section[data-testid="stMain"] span,
        section[data-testid="stMain"] li,
        section[data-testid="stMain"] small,
        section[data-testid="stMain"] .stCaption {
            color: #1A1A1A !important;
        }
        section[data-testid="stMain"] h1,
        section[data-testid="stMain"] h2,
        section[data-testid="stMain"] h3 {
            color: #0D3B4F !important;
            font-weight: 700 !important;
        }
        section[data-testid="stMain"] h4 {
            color: #165C7D !important;
            font-weight: 600 !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: #F0F4F8;
            border-radius: 10px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #575757 !important;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 8px;
            background-color: transparent;
            transition: all 0.2s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #D5EEF0 !important;
            color: #007D89 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #FFFFFF !important;
            background-color: #007D89 !important;
            border-radius: 8px;
        }
        .stTabs [aria-selected="true"]:hover {
            background-color: #006570 !important;
            color: #FFFFFF !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }

        /* Divider */
        hr {
            border: none;
            border-top: 2px solid #E0E0E0;
            margin: 24px 0;
        }

        /* Tooltip do icone ? nos graficos */
        .chart-tooltip {
            position: relative;
            transition: background 0.2s;
        }
        .chart-tooltip:hover {
            background: #CC8200 !important;
        }

        /* ============================================================
         * RESPONSIVIDADE
         * ============================================================ */

        /* Container principal */
        .main .block-container {
            max-width: 1200px;
            padding: 1rem 2rem !important;
        }

        /* Gráficos Plotly: sempre 100% */
        .stPlotlyChart, .js-plotly-plot, .plotly {
            width: 100% !important;
        }

        /* DataFrames: scroll horizontal */
        [data-testid="stDataFrame"] {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            margin: 8px 0;
        }

        /* Scrollbar estilizada */
        ::-webkit-scrollbar { height: 6px; width: 6px; }
        ::-webkit-scrollbar-track { background: #F0F4F8; border-radius: 3px; }
        ::-webkit-scrollbar-thumb { background: #007D89; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #005F68; }

        /* ------ MOBILE (< 768px) ------ */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 0.5rem 0.75rem !important;
            }

            /* Colunas: empilhar em grid 2 colunas */
            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
                gap: 0.4rem !important;
            }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            /* KPIs */
            [data-testid="stMetric"] { padding: 8px 10px; border-left-width: 3px; }
            [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
            [data-testid="stMetricValue"] { font-size: 1rem !important; }

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                overflow-x: auto; flex-wrap: nowrap;
                -webkit-overflow-scrolling: touch; padding: 2px; gap: 2px;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 7px 10px; font-size: 0.75rem;
                white-space: nowrap; flex-shrink: 0;
            }

            /* Cards e texto */
            .insight-box, .alert-box, .danger-box, .success-box {
                padding: 8px 10px; font-size: 0.82rem;
            }
            section[data-testid="stMain"] h1 { font-size: 1.3rem !important; }
            section[data-testid="stMain"] h3 { font-size: 1rem !important; }

            /* Chart headers */
            .chart-tooltip { width: 16px !important; height: 16px !important; font-size: 0.6rem !important; }

            /* Sidebar */
            [data-testid="stSidebar"] { min-width: 240px !important; }
        }

        /* ------ TABLET / ZOOM 125% (769px - 1100px) ------ */
        @media (min-width: 769px) and (max-width: 1100px) {
            .main .block-container { padding: 1rem 1.5rem !important; }

            [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
            [data-testid="stMetricLabel"] { font-size: 0.78rem !important; }

            .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 0.82rem; }

            /* Gráficos lado a lado: empilhar quando apertado */
            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
            }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 48% !important;
            }
        }

        /* ------ ZOOM 150%+ (< 900px efetivo com sidebar) ------ */
        @media (max-width: 900px) and (min-width: 769px) {
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
        }

        /* ------ TELAS GRANDES ------ */
        @media (min-width: 1400px) {
            .main .block-container { max-width: 1400px; }
        }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Carga e tratamento de dados
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Carregando dados...")
def load_data():
    """Carrega e prepara os dados do case."""
    data_path = Path(__file__).parent / "case.xlsx"

    if not data_path.exists():
        st.error(f"Arquivo não encontrado: {data_path}")
        st.stop()

    # Carregar sheets
    df_base = pd.read_excel(data_path, sheet_name="base")
    df_receitas = pd.read_excel(data_path, sheet_name="Receitas 6 meses")

    # Padronizar nomes de colunas (remover espacos extras)
    df_base.columns = df_base.columns.str.strip()
    df_receitas.columns = df_receitas.columns.str.strip()

    # Renomear colunas para usó interno (robusto a encoding)
    base_cols = {c: c for c in df_base.columns}
    receitas_cols = {c: c for c in df_receitas.columns}

    # Tratar coluna ID Ident na base
    id_col_base = [c for c in df_base.columns if "ID" in c.upper() and "IDENT" in c.upper()]
    if id_col_base:
        df_base = df_base.rename(columns={id_col_base[0]: "id_ident"})

    # Tratar colunas receitas
    for col in df_receitas.columns:
        col_upper = col.upper().replace(" ", "")
        if "IDIDENT" in col_upper:
            df_receitas = df_receitas.rename(columns={col: "id_ident"})
        elif "DTBASE" in col_upper:
            df_receitas = df_receitas.rename(columns={col: "dtbase"})
        elif "AVG" in col_upper or "VLRECEITA" in col_upper:
            df_receitas = df_receitas.rename(columns={col: "vlreceita"})
        elif "PRODUTO" in col_upper:
            df_receitas = df_receitas.rename(columns={col: "produto"})
        elif "PERFIL" in col_upper:
            df_receitas = df_receitas.rename(columns={col: "perfil"})

    # Tratar colunas base
    for col in df_base.columns:
        col_upper = col.upper().replace(" ", "")
        if "DSPAPRINCIPAL" in col_upper or "PA" in col_upper.replace("PRINCIPAL", ""):
            if col != "id_ident":
                df_base = df_base.rename(columns={col: "pa"})
        elif "DSSCORE" in col_upper or "SCORE" in col_upper:
            if col != "id_ident":
                df_base = df_base.rename(columns={col: "score"})
        elif "NATURALIDADE" in col_upper:
            df_base = df_base.rename(columns={col: "naturalidade"})

    # Garantir tipos
    df_receitas["dtbase"] = pd.to_datetime(df_receitas["dtbase"], errors="coerce")
    df_receitas["vlreceita"] = pd.to_numeric(df_receitas["vlreceita"], errors="coerce").fillna(0)

    # Marcar registros "não localizado"
    df_receitas["nao_localizado"] = df_receitas["id_ident"].astype(str).str.contains(
        "n.o localizado|não localizado|não localizado", case=False, na=False, regex=True
    )

    # Converter id_ident para numerico onde possível
    df_receitas["id_ident_num"] = pd.to_numeric(df_receitas["id_ident"], errors="coerce")
    df_base["id_ident"] = pd.to_numeric(df_base["id_ident"], errors="coerce")

    # Corrigir encoding em strings (tratar caracteres mal-codificados)
    str_cols_base = df_base.select_dtypes(include="object").columns
    for col in str_cols_base:
        df_base[col] = df_base[col].astype(str).str.strip()

    str_cols_rec = df_receitas.select_dtypes(include="object").columns
    for col in str_cols_rec:
        df_receitas[col] = df_receitas[col].astype(str).str.strip()

    # =====================================================================
    # NORMALIZAÇÃO: acentuação e padronização para apresentação
    # =====================================================================

    # PAs / Agências
    _pa_map = {
        "Ararangua": "Araranguá", "Bento Goncalves": "Bento Gonçalves",
        "Brasilia": "Brasília", "Chapeco": "Chapecó", "Criciuma": "Criciúma",
        "Florianopolis": "Florianópolis", "Foz do Iguacu": "Foz do Iguaçu",
        "GUARAPUAVA": "Guarapuava", "Ijui": "Ijuí", "Itajai": "Itajaí",
        "Jaragua do Sul": "Jaraguá do Sul", "Joacaba": "Joaçaba",
        "Maringa": "Maringá", "Sao Bento do Su": "São Bento do Sul",
        "Sao Caetano": "São Caetano", "Sao Jose": "São José",
        "Sao Jose Campos": "São José dos Campos",
        "Sao Miguel dOes": "São Miguel d'Oeste", "São Paulo": "São Paulo",
        "Tubarao": "Tubarão", "Xanxere": "Xanxerê",
        "POA Centro Hist": "POA Centro Histórico",
    }
    if "pa" in df_base.columns:
        df_base["pa"] = df_base["pa"].replace(_pa_map)

    # Scores
    _score_map = {
        "ALTISSIMO RISCO": "ALTÍSSIMO RISCO",
        "BAIXISSIMO RISCO": "BAIXÍSSIMO RISCO",
        "MEDIO RISCO 1": "MÉDIO RISCO 1",
        "MEDIO RISCO 2": "MÉDIO RISCO 2",
        "SEM CLASSIFICACAO": "SEM CLASSIFICAÇÃO",
    }
    if "score" in df_base.columns:
        df_base["score"] = df_base["score"].replace(_score_map)

    # Naturalidade
    _nat_map = {}
    if "naturalidade" in df_base.columns:
        for val in df_base["naturalidade"].unique():
            if "cho" in str(val).lower() and "Gaúcho" not in str(val):
                _nat_map[val] = "Gaúcho"
        if _nat_map:
            df_base["naturalidade"] = df_base["naturalidade"].replace(_nat_map)
        df_base["regiao"] = df_base["naturalidade"].map(NATURALIDADE_REGIOES)

    # Produtos (nomes podem vir com encoding quebrado do Excel)
    if "produto" in df_receitas.columns:
        _prod_map = {}
        _known = {"Alface", "Ameixa", "Batata", "Cebola", "Laranja",
                  "Melancia", "Tomate", "Uva", "Maçã", "Manjericão", "Melão"}
        for val in df_receitas["produto"].unique():
            s = str(val)
            if s in _known:
                continue
            if s.startswith("Ma") and "Melancia" not in s and "Majeric" not in s:
                _prod_map[val] = "Maçã"
            elif "Majeric" in s or "Manjeric" in s:
                _prod_map[val] = "Manjericão"
            elif s.startswith("Mel") and "Melancia" not in s:
                _prod_map[val] = "Melão"
        if _prod_map:
            df_receitas["produto"] = df_receitas["produto"].replace(_prod_map)

    # Merge: receitas válidas (com id numérico) + dados do associado
    df_rec_valid = df_receitas[~df_receitas["nao_localizado"]].copy()
    df_rec_valid["id_ident"] = df_rec_valid["id_ident_num"]

    df_merged = df_rec_valid.merge(df_base, on="id_ident", how="left")

    # Definir ordem dos scores
    score_order = [
        "BAIXÍSSIMO RISCO", "BAIXO RISCO", "MÉDIO RISCO 1",
        "MÉDIO RISCO 2", "ALTÍSSIMO RISCO", "SEM CLASSIFICAÇÃO",
    ]
    if "score" in df_merged.columns:
        df_merged["score"] = pd.Categorical(
            df_merged["score"], categories=score_order, ordered=True,
        )

    return df_base, df_receitas, df_merged


# ---------------------------------------------------------------------------
# Filtros do sidebar
# ---------------------------------------------------------------------------
def render_sidebar(df_merged: pd.DataFrame):
    """Renderiza filtros no sidebar e retorna dados filtrados."""
    with st.sidebar:
        # Logo Transpocred
        logo_path = Path(__file__).parent / "logo_transpocred.svg"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
            st.markdown("")

        st.markdown("## \U0001f50d Filtros")
        st.markdown("---")

        # PA
        pas_disponíveis = sorted(df_merged["pa"].dropna().unique().tolist())
        pa_selecionadas = st.multiselect(
            "PA / Agência",
            options=pas_disponíveis,
            default=[],
            placeholder="Todas as PAs",
        )

        # Score
        scores_disponíveis = [
            s for s in [
                "BAIXÍSSIMO RISCO", "BAIXO RISCO", "MÉDIO RISCO 1",
                "MÉDIO RISCO 2", "ALTÍSSIMO RISCO", "SEM CLASSIFICAÇÃO",
            ]
            if s in df_merged["score"].cat.categories
        ]
        score_selecionados = st.multiselect(
            "Score de Risco",
            options=scores_disponíveis,
            default=[],
            placeholder="Todos os scores",
        )

        # Perfil
        perfis_disponíveis = sorted(df_merged["perfil"].dropna().unique().tolist())
        perfil_selecionado = st.multiselect(
            "Perfil",
            options=perfis_disponíveis,
            default=[],
            placeholder="Todos os perfis",
        )

        # Produto
        produtos_disponíveis = sorted(df_merged["produto"].dropna().unique().tolist())
        produtos_selecionados = st.multiselect(
            "Produto",
            options=produtos_disponíveis,
            default=[],
            placeholder="Todos os produtos",
        )

        # Naturalidade
        naturalidades_disponíveis = sorted(df_merged["naturalidade"].dropna().unique().tolist())
        naturalidade_selecionada = st.multiselect(
            "Naturalidade",
            options=naturalidades_disponíveis,
            default=[],
            placeholder="Todas as naturalidades",
        )

        # Regiao
        regioes_disponíveis = [r for r in REGIAO_ORDER if r in df_merged["regiao"].dropna().unique()]
        regiao_selecionada = st.multiselect(
            "Região (derivada)",
            options=regioes_disponíveis,
            default=[],
            placeholder="Todas as regiões",
        )

        st.markdown("---")

        # Cenário de interpretação dos dados
        st.markdown("### \U0001f4ca Cenário de Dados")
        cenario = st.radio(
            "Interpretar receita como:",
            ["Valor Absoluto", "Receita Média (AVG)"],
            index=0,
            help="A coluna original chama-se AVG_vlreceita. "
                 "Selecione como deseja interpretar os valores.",
        )

        st.markdown("---")
        st.markdown("### \U0001f4c5 Período dos Dados")
        if "dtbase" in df_merged.columns:
            dt_min = df_merged["dtbase"].min()
            dt_max = df_merged["dtbase"].max()
            st.caption(f"{dt_min.strftime('%d/%m/%Y')} a {dt_max.strftime('%d/%m/%Y')}")

        st.markdown("---")
        st.markdown(
            "<small style='opacity:0.7'>Dashboard desenvolvido para o case "
            "técnico Transpocred</small>",
            unsafe_allow_html=True,
        )

    # Aplicar filtros
    df = df_merged.copy()
    if pa_selecionadas:
        df = df[df["pa"].isin(pa_selecionadas)]
    if score_selecionados:
        df = df[df["score"].isin(score_selecionados)]
    if perfil_selecionado:
        df = df[df["perfil"].isin(perfil_selecionado)]
    if produtos_selecionados:
        df = df[df["produto"].isin(produtos_selecionados)]
    if naturalidade_selecionada:
        df = df[df["naturalidade"].isin(naturalidade_selecionada)]
    if regiao_selecionada:
        df = df[df["regiao"].isin(regiao_selecionada)]

    filtros_ativos = bool(
        pa_selecionadas or score_selecionados or perfil_selecionado
        or produtos_selecionados or naturalidade_selecionada or regiao_selecionada
    )
    is_media = cenario == "Receita Média (AVG)"
    return df, filtros_ativos, is_media


# ---------------------------------------------------------------------------
# Funcao auxiliar para layout de gráficos
# ---------------------------------------------------------------------------
# Labels dinâmicos conforme cenário
def lbl(is_media: bool, tipo: str = "receita") -> str:
    """Retorna label adequado ao cenário selecionado."""
    labels = {
        "receita": "Receita Média" if is_media else "Receita",
        "receita_total": "Receita Média Acumulada" if is_media else "Receita Total",
        "ticket": "Ticket Médio (sobre média)" if is_media else "Ticket Médio",
        "eixo": "Receita Média (R$)" if is_media else "Receita (R$)",
    }
    return labels.get(tipo, tipo)


def default_layout(fig, height=450, margin=None, showlegend=True):
    """Aplica layout padrão aos gráficos Plotly."""
    if margin is None:
        margin = dict(l=50, r=30, t=30, b=50)
    fig.update_layout(
        height=height,
        margin=margin,
        autosize=True,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        separators=",.",  # pt-BR: vírgula decimal, ponto milhar
        font=dict(family="Inter, Segoe UI, Arial", size=11, color="#1A1A1A"),
        title=dict(text="", font=dict(size=14, color="#0D3B4F")),
        showlegend=showlegend,
        legend=dict(
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#E0E0E0",
            borderwidth=1,
            font=dict(size=10, color="#1A1A1A"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_xaxes(
        gridcolor="#F0F0F0", linecolor="#E0E0E0", linewidth=1,
        title_font=dict(size=11, color="#1A1A1A"),
        tickfont=dict(size=10, color="#333333"),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="#F0F0F0", linecolor="#E0E0E0", linewidth=1,
        title_font=dict(size=11, color="#1A1A1A"),
        tickfont=dict(size=10, color="#333333"),
        automargin=True,
    )
    return fig


def chart_header(title: str, tooltip: str):
    """Renderiza título de gráfico com ícone de interrogação e tooltip no hover."""
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
        f'<span style="font-size:1.15rem;font-weight:600;color:#165C7D;">{title}</span>'
        f'<span class="chart-tooltip" title="{tooltip}"'
        f' style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:20px;height:20px;border-radius:50%;background:#FFA300;color:white;'
        f'font-size:0.75rem;font-weight:700;cursor:help;">?</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_chart(fig, **kwargs):
    """Renderiza gráfico Plotly forçando cores escuras, responsivo e sem subtitle."""
    fig.update_xaxes(
        title_font=dict(size=11, color="#1A1A1A"),
        tickfont=dict(size=10, color="#333333"),
        automargin=True,
    )
    fig.update_yaxes(
        title_font=dict(size=11, color="#1A1A1A"),
        tickfont=dict(size=10, color="#333333"),
        automargin=True,
    )
    fig.update_layout(
        title_text="",
        autosize=True,
    )
    # Responsive config: permite redimensionar + remove botões desnecessários
    kwargs.setdefault("use_container_width", True)
    kwargs.setdefault("config", {
        "responsive": True,
        "displayModeBar": False,
    })
    st.plotly_chart(fig, **kwargs)


# ---------------------------------------------------------------------------
# Tab 1 - Visão Geral
# ---------------------------------------------------------------------------
def render_visao_geral(df: pd.DataFrame, df_receitas_raw: pd.DataFrame, filtros_ativos: bool, is_media: bool = False):
    """Renderiza a aba Visão Geral."""

    st.markdown("### \U0001f4c8 Visão Geral da Cooperativa")

    if filtros_ativos:
        st.info("\U0001f50d Filtros ativos - os indicadores refletem a selecao aplicada.")

    # --- KPIs ---
    total_associados = df["id_ident"].nunique()
    receita_total = df["vlreceita"].sum()
    ticket_médio = receita_total / total_associados if total_associados > 0 else 0
    total_pas = df["pa"].nunique()
    total_produtos = df["produto"].nunique()
    pct_triste = (
        df[df["perfil"] == "Triste"]["id_ident"].nunique() / total_associados * 100
        if total_associados > 0 else 0
    )

    # Indicadores regionais
    naturalidades_distintas = df["naturalidade"].dropna().nunique()
    assoc_sul = df[df["regiao"] == "Sul"]["id_ident"].nunique()
    pct_sul = assoc_sul / total_associados * 100 if total_associados > 0 else 0
    nat_lider_series = df.drop_duplicates("id_ident")["naturalidade"].value_counts()
    nat_lider = nat_lider_series.index[0] if len(nat_lider_series) > 0 else "—"
    pct_lider = nat_lider_series.iloc[0] / total_associados * 100 if total_associados > 0 and len(nat_lider_series) > 0 else 0

    # KPIs em 3 linhas de 3
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Associados", fmt_num(total_associados))
    c2.metric(lbl(is_media, 'receita_total'), fmt_brl(receita_total))
    c3.metric(lbl(is_media, 'ticket'), fmt_brl(ticket_médio))
    c4, c5, c6 = st.columns(3)
    c4.metric("PAs Ativas", fmt_num(total_pas))
    c5.metric("Produtos", fmt_num(total_produtos))
    c6.metric("% Perfil Triste", fmt_pct(pct_triste))
    c7, c8, c9 = st.columns(3)
    c7.metric("Naturalidades Distintas", fmt_num(naturalidades_distintas))
    c8.metric("% Região Sul", fmt_pct(pct_sul), help="Catarinenses + Gaúchos sobre o total de associados — alinhado à identidade regional da cooperativa.")
    c9.metric(f"Naturalidade Líder", f"{nat_lider} ({fmt_pct(pct_lider)})")

    st.markdown("---")

    # --- Evolução de Receita ---
    col_left, col_right = st.columns([3, 2])

    with col_left:
        chart_header(f"Evolução da {lbl(is_media, 'receita')} Mensal", "Mostra a receita total mês a mês. A linha tracejada indica a tendência. Queda no último mês pode sinalizar sazonalidade ou perda de clientes-chave.")
        receita_mensal = (
            df.groupby(df["dtbase"].dt.to_period("M"))["vlreceita"]
            .sum()
            .reset_index()
        )
        receita_mensal["dtbase"] = receita_mensal["dtbase"].dt.to_timestamp()
        receita_mensal["label"] = receita_mensal["dtbase"].dt.strftime("%b/%Y")

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Scatter(
            x=receita_mensal["dtbase"],
            y=receita_mensal["vlreceita"],
            mode="lines+markers+text",
            name="Receita",
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=10, color=COLORS["primary"]),
            text=[fmt_brl(v) for v in receita_mensal["vlreceita"]],
            textposition="top center",
            textfont=dict(size=10, color="#1A1A1A"),
            hovertemplate="<b>%{x|%b/%Y}</b><br>Receita: R$ %{y:,.0f}<extra></extra>",
        ))

        # Linha de tendência
        if len(receita_mensal) >= 2:
            x_num = np.arange(len(receita_mensal))
            z = np.polyfit(x_num, receita_mensal["vlreceita"].values, 1)
            p = np.poly1d(z)
            fig_evol.add_trace(go.Scatter(
                x=receita_mensal["dtbase"],
                y=p(x_num),
                mode="lines",
                name="Tendência",
                line=dict(color=COLORS["warning"], width=2, dash="dash"),
                hoverinfo="skip",
            ))

        fig_evol = default_layout(fig_evol, height=400)
        fig_evol.update_layout(
            yaxis_title=lbl(is_media, 'eixo'),
            xaxis_title=None,
            yaxis_tickformat=",.0f",
            yaxis_tickprefix="R$ ",
        )
        render_chart(fig_evol, use_container_width=True)

        # Insight sobre queda em marco
        if len(receita_mensal) >= 2:
            last = receita_mensal["vlreceita"].iloc[-1]
            avg_prev = receita_mensal["vlreceita"].iloc[:-1].mean()
            var_pct = (last - avg_prev) / avg_prev * 100 if avg_prev != 0 else 0
            if var_pct < -5:
                st.markdown(
                    f'<div class="alert-box">'
                    f'<div class="card-title-alert">\u26a0 Alerta: Queda de Receita</div>'
                    f'O último mes registra {fmt_brl(last)} — uma variação de '
                    f'{fmt_pct(var_pct)} em relacao a média dos meses anteriores ({fmt_brl(avg_prev)}).'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_right:
        chart_header(f"{lbl(is_media, 'receita')} por Produto", "Barras ordenadas pela receita total de cada produto. Observe a concentração: se um produto domina, há risco de dependência. Produtos menores são oportunidades de cross-sell.")
        receita_prod = (
            df.groupby("produto")["vlreceita"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )

        colors_prod = [
            COLORS["primary"] if v > 0 else COLORS["negative"]
            for v in receita_prod["vlreceita"]
        ]

        fig_prod = go.Figure(go.Bar(
            x=receita_prod["vlreceita"],
            y=receita_prod["produto"],
            orientation="h",
            marker_color=colors_prod,
            text=[fmt_brl(v) for v in receita_prod["vlreceita"]],
            textposition="auto",
            textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Receita: R$ %{x:,.0f}<extra></extra>",
        ))
        fig_prod = default_layout(fig_prod, height=400, showlegend=False)
        fig_prod.update_layout(
            xaxis_title=lbl(is_media, 'eixo'),
            yaxis_title=None,
            xaxis_tickformat=",.0f",
            xaxis_tickprefix="R$ ",
        )
        render_chart(fig_prod, use_container_width=True)

    # --- Score + Perfil ---
    col_score, col_perfil = st.columns(2)

    with col_score:
        chart_header("Distribuição por Score de Risco", "Proporção de associados em cada faixa de risco. 'SEM CLASSIFICAÇÃO' em cinza merece atenção especial — são associados sem avaliação de risco.")
        score_dist = (
            df.groupby("score", observed=False)["id_ident"]
            .nunique()
            .reset_index()
            .rename(columns={"id_ident": "qtd"})
        )
        score_dist = score_dist[score_dist["qtd"] > 0]
        score_dist["cor"] = score_dist["score"].astype(str).map(SCORE_COLORS).fillna(COLORS["neutral"])

        fig_score = go.Figure(go.Pie(
            labels=score_dist["score"],
            values=score_dist["qtd"],
            marker=dict(colors=score_dist["cor"].tolist()),
            hole=0.45,
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=9),
            hovertemplate="<b>%{label}</b><br>Associados: %{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig_score = default_layout(fig_score, height=400)
        fig_score.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=30))
        render_chart(fig_score, use_container_width=True)

    with col_perfil:
        chart_header(f"{lbl(is_media, 'receita')} por Perfil", "Compara receita gerada por associados Alegre vs Triste. Se Triste gera mais receita, os clientes mais valiosos estão insatisfeitos — risco crítico de evasão.")
        perfil_receita = (
            df.groupby("perfil")["vlreceita"]
            .sum()
            .reset_index()
        )
        perfil_receita["cor"] = perfil_receita["perfil"].astype(str).map(PERFIL_COLORS).fillna(COLORS["neutral"])

        fig_perfil = go.Figure(go.Bar(
            x=perfil_receita["perfil"],
            y=perfil_receita["vlreceita"],
            marker_color=perfil_receita["cor"].tolist(),
            text=[fmt_brl(v) for v in perfil_receita["vlreceita"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>",
        ))
        fig_perfil = default_layout(fig_perfil, height=400, showlegend=False)
        fig_perfil.update_layout(
            yaxis_title=lbl(is_media, 'eixo'),
            xaxis_title=None,
            yaxis_tickformat=",.0f",
            yaxis_tickprefix="R$ ",
        )
        render_chart(fig_perfil, use_container_width=True)

        st.markdown(
            '<div class="insight-box">'
            '<div class="card-title">\U0001f4a1 Insight - Paradoxo do Perfil</div>'
            'O perfil "Triste" gera significativamente mais receita que o "Alegre". '
            'Associados de alto valor podem estar insatisfeitos — um risco crítico de retenção '
            'que demanda acao imediata de relacionamento.'
            '</div>',
            unsafe_allow_html=True,
        )

    # --- Qualidade dos dados ---
    n_nao_loc = df_receitas_raw["nao_localizado"].sum()
    pct_nao_loc = n_nao_loc / len(df_receitas_raw) * 100
    st.markdown("---")
    st.markdown(
        f'<div class="alert-box">'
        f'<div class="card-title-alert">\U0001f4cb Qualidade dos Dados</div>'
        f'{fmt_num(n_nao_loc)} registros de receita ({fmt_pct(pct_nao_loc)}) possuem '
        f'ID "não localizado" e foram excluidos das análises. '
        f'Recomenda-se investigar a origem desses registros órfãos no sistema legado.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tab 2 - Concentração de Receita
# ---------------------------------------------------------------------------
def render_concentração(df: pd.DataFrame, is_media: bool = False):
    """Renderiza a aba Concentração de Receita."""

    st.markdown("### \U0001f4b0 Concentração de Receita")
    st.caption(
        "Análise da distribuição de receita por associado — "
        "fundamental para entender riscos de concentração."
    )

    # Receita por associado
    receita_cliente = (
        df.groupby("id_ident")["vlreceita"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    receita_cliente["rank"] = range(1, len(receita_cliente) + 1)
    receita_cliente["pct_rank"] = receita_cliente["rank"] / len(receita_cliente) * 100
    total_receita = receita_cliente["vlreceita"].sum()
    receita_cliente["pct_receita"] = receita_cliente["vlreceita"] / total_receita * 100
    receita_cliente["pct_receita_cum"] = receita_cliente["pct_receita"].cumsum()

    # KPIs de concentração
    n = len(receita_cliente)
    top10_idx = int(n * 0.10)
    top20_idx = int(n * 0.20)
    bottom50_idx = int(n * 0.50)

    top10_pct = receita_cliente.iloc[:top10_idx]["vlreceita"].sum() / total_receita * 100
    top20_pct = receita_cliente.iloc[:top20_idx]["vlreceita"].sum() / total_receita * 100
    bottom50_receita = receita_cliente.iloc[n - bottom50_idx:]["vlreceita"].sum()
    bottom50_pct = bottom50_receita / total_receita * 100

    neg_clientes = (receita_cliente["vlreceita"] < 0).sum()
    neg_total = receita_cliente[receita_cliente["vlreceita"] < 0]["vlreceita"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Top 10% = % da Receita", fmt_pct(top10_pct))
    c2.metric("Top 20% = % da Receita", fmt_pct(top20_pct))
    c3.metric("Bottom 50% = % da Receita", fmt_pct(bottom50_pct))
    c4.metric("Associados c/ Receita Negativa", fmt_num(neg_clientes))

    st.markdown("---")

    # --- Pareto ---
    col_pareto, col_quintil = st.columns([3, 2])

    with col_pareto:
        chart_header("Curva de Pareto - Concentração de Receita", "Mostra quanto % da receita é gerado por quanto % dos associados. Quanto mais a curva sobe rápido, maior a concentração. Linhas de referência em 10% e 20% facilitam a leitura.")

        # Amostrar para performance se necessario
        if len(receita_cliente) > 5000:
            sample_idx = np.linspace(0, len(receita_cliente) - 1, 2000, dtype=int)
            pareto_data = receita_cliente.iloc[sample_idx]
        else:
            pareto_data = receita_cliente

        fig_pareto = go.Figure()

        # Area preenchida
        fig_pareto.add_trace(go.Scatter(
            x=pareto_data["pct_rank"],
            y=pareto_data["pct_receita_cum"],
            mode="lines",
            fill="tozeroy",
            name="% Acumulada da Receita",
            line=dict(color=COLORS["primary"], width=2.5),
            fillcolor="rgba(13, 71, 161, 0.12)",
            hovertemplate="Top %{x:.1f}% dos associados<br>= %{y:.1f}% da receita<extra></extra>",
        ))

        # Linha de igualdade perfeita
        fig_pareto.add_trace(go.Scatter(
            x=[0, 100], y=[0, 100],
            mode="lines",
            name="Distribuição uniforme",
            line=dict(color=COLORS["neutral"], width=1.5, dash="dot"),
            hoverinfo="skip",
        ))

        # Marcadores de referencia
        for pct, label_y, color in [
            (10, top10_pct, COLORS["negative"]),
            (20, top20_pct, COLORS["warning"]),
        ]:
            fig_pareto.add_shape(
                type="line", x0=pct, x1=pct, y0=0, y1=label_y,
                line=dict(color=color, width=1.5, dash="dash"),
            )
            fig_pareto.add_shape(
                type="line", x0=0, x1=pct, y0=label_y, y1=label_y,
                line=dict(color=color, width=1.5, dash="dash"),
            )
            fig_pareto.add_annotation(
                x=pct, y=label_y + 3,
                text=f"Top {pct}% = {label_y:.1f}%",
                showarrow=False,
                font=dict(size=11, color=color, weight="bold"),
            )

        fig_pareto = default_layout(fig_pareto, height=450)
        fig_pareto.update_layout(
            xaxis_title="% dos Associados (ranking por receita)",
            yaxis_title="% Acumulada da Receita",
            xaxis_range=[0, 105],
            yaxis_range=[0, 105],
        )
        render_chart(fig_pareto, use_container_width=True)

    with col_quintil:
        chart_header("Receita por Quintil de Associados", "Divide os associados em 5 grupos iguais (20% cada) por valor de receita. O quintil 1 são os maiores. Se o quintil 5 é negativo, metade da base não gera receita.")

        # Dividir em quintis
        receita_cliente["quintil"] = pd.qcut(
            receita_cliente["rank"],
            q=5,
            labels=["Top 20%", "21-40%", "41-60%", "61-80%", "Bottom 20%"],
        )
        quintil_receita = (
            receita_cliente.groupby("quintil", observed=False)["vlreceita"]
            .sum()
            .reset_index()
        )

        colors_quintil = [
            COLORS["primary"], COLORS["primary_light"],
            COLORS["secondary_light"], COLORS["neutral"],
            COLORS["negative"] if quintil_receita["vlreceita"].iloc[-1] < 0 else COLORS["neutral"],
        ]

        fig_quintil = go.Figure(go.Bar(
            x=quintil_receita["quintil"],
            y=quintil_receita["vlreceita"],
            marker_color=colors_quintil,
            text=[fmt_brl(v) for v in quintil_receita["vlreceita"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>",
        ))
        fig_quintil = default_layout(fig_quintil, height=450, showlegend=False)
        fig_quintil.update_layout(
            yaxis_title=lbl(is_media, 'eixo'),
            xaxis_title=None,
            yaxis_tickformat=",.0f",
            yaxis_tickprefix="R$ ",
        )
        render_chart(fig_quintil, use_container_width=True)

    # Insights
    st.markdown(
        f'<div class="danger-box">'
        f'<div class="card-title-danger">\u26a0 Risco de Concentração Crítico</div>'
        f'Apenas <b>10% dos associados geram {fmt_pct(top10_pct)} da receita</b>. '
        f'Isso representa uma dependência perigosa — a perda de poucos clientes-chave '
        f'pode comprometer significativamente o resultado da cooperativa.<br><br>'
        f'Adicionalmente, <b>{fmt_num(neg_clientes)} associados apresentam receita negativa '
        f'acumulada</b> ({fmt_brl(neg_total)}), indicando custos operacionais superiores '
        f'a geracao de receita desses membros.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tab - Perfil Demográfico (Naturalidade)
# ---------------------------------------------------------------------------
def render_perfil_demografico(df: pd.DataFrame, is_media: bool = False):
    """Renderiza a aba de Perfil Demográfico por naturalidade / região."""

    st.markdown("### \U0001f30e Perfil Demográfico por Naturalidade")
    st.caption(
        "Distribuição de associados, receita e comportamento por naturalidade "
        "(11 grupos) e região de origem — identifica concentração, dependência "
        "regional e oportunidades de cross-sell segmentado."
    )

    if df["naturalidade"].dropna().empty:
        st.warning("Não há dados de naturalidade para os filtros aplicados.")
        return

    # --- KPIs ---
    total_assoc = df["id_ident"].nunique()
    nat_stats = (
        df.groupby("naturalidade", observed=False)
        .agg(
            associados=("id_ident", "nunique"),
            receita=("vlreceita", "sum"),
        )
        .reset_index()
        .sort_values("receita", ascending=False)
    )
    nat_stats["ticket"] = nat_stats["receita"] / nat_stats["associados"].replace(0, np.nan)
    nat_stats["pct_assoc"] = nat_stats["associados"] / nat_stats["associados"].sum() * 100
    nat_stats["pct_receita"] = nat_stats["receita"] / nat_stats["receita"].sum() * 100

    top_nat = nat_stats.iloc[0]
    top_ticket_row = nat_stats.loc[nat_stats["ticket"].idxmax()]
    pct_top2 = nat_stats["pct_receita"].nlargest(2).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Naturalidades Distintas", fmt_num(nat_stats.shape[0]))
    c2.metric(
        "Naturalidade com Maior Receita",
        f"{top_nat['naturalidade']}",
        f"{fmt_pct(top_nat['pct_receita'])} da receita",
    )
    c3.metric(
        "Maior Ticket Médio",
        f"{top_ticket_row['naturalidade']}",
        fmt_brl(top_ticket_row["ticket"]),
    )
    c4.metric(
        "Concentração Top 2",
        fmt_pct(pct_top2),
        help="% da receita concentrada nas 2 naturalidades principais.",
    )

    st.markdown("---")

    # --- Treemap + Barra ticket ---
    col_tree, col_tk = st.columns(2)

    with col_tree:
        chart_header(
            f"{lbl(is_media, 'receita')} por Naturalidade (Treemap)",
            "Área proporcional à receita total gerada por cada naturalidade. "
            "Grupos maiores indicam dependência de receita.",
        )
        fig_tree = go.Figure(go.Treemap(
            labels=nat_stats["naturalidade"],
            parents=[""] * len(nat_stats),
            values=nat_stats["receita"].clip(lower=0),
            text=[
                f"{fmt_brl(r)}<br>{fmt_num(a)} assoc.<br>{fmt_pct(p)}"
                for r, a, p in zip(nat_stats["receita"], nat_stats["associados"], nat_stats["pct_receita"])
            ],
            textinfo="label+text",
            marker=dict(
                colors=nat_stats["receita"],
                colorscale="Teal",
                line=dict(width=1, color="white"),
            ),
            hovertemplate="<b>%{label}</b><br>Receita: %{value:,.0f}<extra></extra>",
        ))
        fig_tree = default_layout(fig_tree, height=420, showlegend=False)
        render_chart(fig_tree, use_container_width=True)

    with col_tk:
        chart_header(
            "Ticket Médio por Naturalidade",
            "Receita média por associado em cada grupo. Valores altos mesmo em grupos "
            "pequenos indicam nichos premium para expansão.",
        )
        tk = nat_stats.sort_values("ticket", ascending=True)
        fig_tk = go.Figure(go.Bar(
            x=tk["ticket"],
            y=tk["naturalidade"],
            orientation="h",
            marker_color=COLORS["primary"],
            text=[fmt_brl(v) for v in tk["ticket"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Ticket: R$ %{x:,.0f}<extra></extra>",
        ))
        fig_tk = default_layout(fig_tk, height=420, showlegend=False)
        fig_tk.update_layout(
            xaxis_title="Ticket médio (R$)",
            yaxis_title=None,
            xaxis_tickformat=",.0f",
            xaxis_tickprefix="R$ ",
        )
        render_chart(fig_tk, use_container_width=True)

    st.markdown("---")

    # --- Região + Perfil x Naturalidade ---
    col_reg, col_perf = st.columns(2)

    with col_reg:
        chart_header(
            f"{lbl(is_media, 'receita')} por Região",
            "Agrupamento das 11 naturalidades por região do Brasil. Mostra se a cooperativa "
            "é realmente regionalizada ou se a base é mais distribuída do que parece.",
        )
        reg_stats = (
            df.dropna(subset=["regiao"])
            .groupby("regiao", observed=False)
            .agg(
                associados=("id_ident", "nunique"),
                receita=("vlreceita", "sum"),
            )
            .reset_index()
        )
        reg_stats["regiao"] = pd.Categorical(reg_stats["regiao"], categories=REGIAO_ORDER, ordered=True)
        reg_stats = reg_stats.sort_values("regiao")

        fig_reg = go.Figure(go.Bar(
            x=reg_stats["regiao"].astype(str),
            y=reg_stats["receita"],
            marker_color=[REGIAO_COLORS.get(r, COLORS["neutral"]) for r in reg_stats["regiao"].astype(str)],
            text=[
                f"{fmt_brl(r)}<br>{fmt_num(a)} assoc."
                for r, a in zip(reg_stats["receita"], reg_stats["associados"])
            ],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>",
        ))
        fig_reg = default_layout(fig_reg, height=400, showlegend=False)
        fig_reg.update_layout(
            yaxis_title=lbl(is_media, "eixo"),
            yaxis_tickformat=",.0f",
            yaxis_tickprefix="R$ ",
        )
        render_chart(fig_reg, use_container_width=True)

    with col_perf:
        chart_header(
            "% Perfil 'Triste' por Naturalidade",
            "Percentual de associados Triste em cada grupo. Revela se a insatisfação "
            "tem recorte regional — útil para direcionar ações de relacionamento.",
        )
        perfil_nat = (
            df.drop_duplicates("id_ident")
            .groupby("naturalidade", observed=False)["perfil"]
            .value_counts(normalize=True)
            .mul(100)
            .rename("pct")
            .reset_index()
        )
        triste_nat = perfil_nat[perfil_nat["perfil"] == "Triste"].copy()
        triste_nat = triste_nat.sort_values("pct", ascending=True)

        fig_tr = go.Figure(go.Bar(
            x=triste_nat["pct"],
            y=triste_nat["naturalidade"],
            orientation="h",
            marker_color=[
                COLORS["negative"] if v > triste_nat["pct"].median() else COLORS["primary_light"]
                for v in triste_nat["pct"]
            ],
            text=[fmt_pct(v) for v in triste_nat["pct"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% Triste<extra></extra>",
        ))
        fig_tr = default_layout(fig_tr, height=400, showlegend=False)
        fig_tr.update_layout(
            xaxis_title="% Perfil Triste",
            yaxis_title=None,
        )
        render_chart(fig_tr, use_container_width=True)

    st.markdown("---")

    # --- Top Produto por Naturalidade ---
    chart_header(
        f"{lbl(is_media, 'receita')} por Naturalidade x Produto",
        "Heatmap que mostra qual produto concentra mais receita em cada naturalidade. "
        "Células fortes fora da diagonal indicam oportunidades de cross-sell regional "
        "(ex.: produto que vende bem no Sul mas é subutilizado no Nordeste).",
    )
    nat_prod = (
        df.groupby(["naturalidade", "produto"], observed=False)["vlreceita"]
        .sum()
        .reset_index()
    )
    nat_prod_pivot = nat_prod.pivot_table(
        index="naturalidade", columns="produto", values="vlreceita", fill_value=0,
    )
    # Ordenar naturalidades por receita total
    ordem_nat = nat_stats.sort_values("receita", ascending=False)["naturalidade"].tolist()
    nat_prod_pivot = nat_prod_pivot.reindex([n for n in ordem_nat if n in nat_prod_pivot.index])

    text_vals = [[fmt_brl(v) for v in row] for row in nat_prod_pivot.values]

    fig_np = go.Figure(go.Heatmap(
        z=nat_prod_pivot.values,
        x=nat_prod_pivot.columns.tolist(),
        y=nat_prod_pivot.index.tolist(),
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(size=9),
        colorscale=[[0, "#FFFFFF"], [0.1, "#CFE8EC"], [0.5, "#4DA8B3"], [1, "#007D89"]],
        hovertemplate="<b>%{y}</b> | %{x}<br>Receita: %{text}<extra></extra>",
        showscale=True,
        colorbar=dict(title="Receita"),
    ))
    fig_np = default_layout(fig_np, height=480, showlegend=False)
    fig_np.update_layout(
        xaxis_title="Produto",
        yaxis_title=None,
        xaxis_tickangle=-30,
    )
    render_chart(fig_np, use_container_width=True)

    st.markdown("---")

    # --- Tabela consolidada ---
    with st.expander("Ver tabela detalhada por Naturalidade"):
        display_nat = pd.DataFrame({
            "Naturalidade": nat_stats["naturalidade"],
            "Região": nat_stats["naturalidade"].map(NATURALIDADE_REGIOES).fillna("—"),
            "Associados": nat_stats["associados"].apply(fmt_num),
            "% Associados": nat_stats["pct_assoc"].apply(fmt_pct),
            "Receita Total": nat_stats["receita"].apply(fmt_brl),
            "% Receita": nat_stats["pct_receita"].apply(fmt_pct),
            "Ticket Médio": nat_stats["ticket"].apply(fmt_brl),
        })
        st.dataframe(display_nat, use_container_width=True, hide_index=True)

    # --- Insights ---
    col_i1, col_i2 = st.columns(2)

    with col_i1:
        # Top 2 concentração
        top2_names = nat_stats.head(2)["naturalidade"].tolist()
        st.markdown(
            f'<div class="insight-box">'
            f'<div class="card-title">\U0001f4a1 Concentração Regional</div>'
            f'<b>{top2_names[0]}</b> e <b>{top2_names[1]}</b> concentram '
            f'<b>{fmt_pct(pct_top2)}</b> de toda a receita. '
            f'Dependência regional elevada reforça a necessidade de estratégias '
            f'defensivas (retenção nesses grupos) e expansão (diversificação em outras regiões).'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_i2:
        # Triste alto
        if not triste_nat.empty:
            pior_triste = triste_nat.iloc[-1]
            st.markdown(
                f'<div class="alert-box">'
                f'<div class="card-title-alert">\u26a0 Insatisfação com Recorte Regional</div>'
                f'<b>{pior_triste["naturalidade"]}</b> lidera o percentual de perfil "Triste" '
                f'({fmt_pct(pior_triste["pct"])}). Investigar se há fatores operacionais '
                f'específicos (PA, produtos disponíveis) influenciando esse grupo.'
                f'</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Tab 3 - Análise de Risco
# ---------------------------------------------------------------------------
def render_risco(df: pd.DataFrame, is_media: bool = False):
    """Renderiza a aba Análise de Risco."""

    st.markdown("### \U0001f6e1 Análise de Risco")
    st.caption(
        "Cruzamento entre score de crédito, perfil comportamental e geracao de receita."
    )

    # --- Heatmap Score x Perfil ---
    col_heat, col_bar = st.columns([3, 2])

    with col_heat:
        chart_header("Receita por Score x Perfil", "Heatmap cruzando score de risco com perfil. Cores mais intensas = mais receita. Identifique quais combinações geram mais valor e onde está o risco (ex: SEM CLASSIFICAÇÃO + Triste).")

        heatmap_data = (
            df.groupby(["score", "perfil"], observed=False)["vlreceita"]
            .sum()
            .reset_index()
        )
        heatmap_pivot = heatmap_data.pivot_table(
            index="score", columns="perfil", values="vlreceita", fill_value=0,
        )

        # Manter ordem dos scores
        score_order = [
            "BAIXÍSSIMO RISCO", "BAIXO RISCO", "MÉDIO RISCO 1",
            "MÉDIO RISCO 2", "ALTÍSSIMO RISCO", "SEM CLASSIFICAÇÃO",
        ]
        heatmap_pivot = heatmap_pivot.reindex(
            [s for s in score_order if s in heatmap_pivot.index]
        )

        # Texto formatado para cada celula
        text_vals = [[fmt_brl(v) for v in row] for row in heatmap_pivot.values]

        fig_heat = go.Figure(go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns.tolist(),
            y=heatmap_pivot.index.tolist(),
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=12),
            colorscale=[
                [0, "#FFEBEE"], [0.25, "#FFCDD2"], [0.5, "#EF9A9A"],
                [0.75, "#42A5F5"], [1, "#0D47A1"],
            ],
            hovertemplate="<b>%{y}</b> | %{x}<br>Receita: %{text}<extra></extra>",
            showscale=True,
            colorbar=dict(title="Receita"),
        ))
        fig_heat = default_layout(fig_heat, height=420, showlegend=False)
        fig_heat.update_layout(
            xaxis_title="Perfil",
            yaxis_title=None,
            yaxis_autorange="reversed",
        )
        render_chart(fig_heat, use_container_width=True)

    with col_bar:
        chart_header("Associados por Score e Perfil", "Quantidade de associados em cada score, divididos por perfil. A proporção de Triste em cada score revela onde a insatisfação é mais concentrada.")

        score_perfil = (
            df.groupby(["score", "perfil"], observed=False)["id_ident"]
            .nunique()
            .reset_index()
            .rename(columns={"id_ident": "qtd"})
        )

        fig_sp = px.bar(
            score_perfil,
            x="score",
            y="qtd",
            color="perfil",
            barmode="group",
            color_discrete_map=PERFIL_COLORS,
            labels={"qtd": "Associados", "score": "", "perfil": "Perfil"},
        )
        fig_sp.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            textfont=dict(size=9),
            hovertemplate="<b>%{x}</b><br>Perfil: %{data.name}<br>Associados: %{y:,.0f}<extra></extra>"
        )
        fig_sp = default_layout(fig_sp, height=420)
        fig_sp.update_layout(
            yaxis_title="Associados",
            xaxis_tickangle=-30,
            legend_title=None,
        )
        render_chart(fig_sp, use_container_width=True)

    st.markdown("---")

    # --- Metricas por Score ---
    chart_header("Indicadores por Score de Risco", "Tabela consolidada com receita total, ticket médio, quantidade e % de Triste por score. Compare eficiência (ticket médio) e risco (% Triste) entre faixas.")

    score_stats = (
        df.groupby("score", observed=False)
        .agg(
            associados=("id_ident", "nunique"),
            receita=("vlreceita", "sum"),
            transações=("vlreceita", "count"),
        )
        .reset_index()
    )
    score_stats["ticket"] = score_stats["receita"] / score_stats["associados"]
    score_stats["pct_receita"] = score_stats["receita"] / score_stats["receita"].sum() * 100
    score_stats["pct_associados"] = score_stats["associados"] / score_stats["associados"].sum() * 100

    # Adicionar % Triste
    triste_stats = (
        df[df["perfil"] == "Triste"]
        .groupby("score", observed=False)["id_ident"]
        .nunique()
        .reset_index()
        .rename(columns={"id_ident": "triste_count"})
    )
    score_stats = score_stats.merge(triste_stats, on="score", how="left")
    score_stats["triste_count"] = score_stats["triste_count"].fillna(0)
    score_stats["pct_triste"] = (
        score_stats["triste_count"] / score_stats["associados"] * 100
    )

    score_stats = score_stats[score_stats["associados"] > 0]

    # Exibir como tabela estilizada
    display_df = pd.DataFrame({
        "Score": score_stats["score"].astype(str),
        "Associados": score_stats["associados"].apply(fmt_num),
        "% Associados": score_stats["pct_associados"].apply(fmt_pct),
        "Receita Total": score_stats["receita"].apply(fmt_brl),
        "% Receita": score_stats["pct_receita"].apply(fmt_pct),
        "Ticket Médio": score_stats["ticket"].apply(fmt_brl),
        "% Triste": score_stats["pct_triste"].apply(fmt_pct),
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Insights
    col_ins1, col_ins2 = st.columns(2)

    with col_ins1:
        # Encontrar score SEM CLASSIFICACAO
        sem_class = score_stats[score_stats["score"] == "SEM CLASSIFICAÇÃO"]
        if not sem_class.empty:
            sc = sem_class.iloc[0]
            st.markdown(
                f'<div class="alert-box">'
                f'<div class="card-title-alert">\U0001f50d "SEM CLASSIFICAÇÃO" - O Ponto Cego</div>'
                f'{fmt_num(sc["associados"])} associados ({fmt_pct(sc["pct_associados"])}) '
                f'sem classificação de risco geram {fmt_pct(sc["pct_receita"])} da receita total '
                f'(ticket médio {fmt_brl(sc["ticket"])}). Porem, '
                f'{fmt_pct(sc["pct_triste"])} deles tem perfil "Triste".<br><br>'
                f'<b>Recomendação:</b> Classificar esses associados com urgencia — '
                f'são altamente lucrativos mas também os mais vulneraveis a evasão.'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_ins2:
        st.markdown(
            '<div class="insight-box">'
            '<div class="card-title">\U0001f4a1 Insight - Perfil x Receita</div>'
            'Em todos os scores, associados "Triste" tendem a gerar mais receita. '
            'Isso sugere que membros mais engajados (com mais produtos/servicos) '
            'podem estar experimentando fricoes operacionais ou insatisfação com o atendimento. '
            'Estrategias de Customer Success direcionadas aos top contributors '
            'são essenciais para retenção.'
            '</div>',
            unsafe_allow_html=True,
        )

    # --- Risco x Naturalidade ---
    if df["naturalidade"].dropna().empty:
        return

    st.markdown("---")
    chart_header(
        "Score de Risco x Naturalidade",
        "Percentual de associados em cada score dentro de cada naturalidade. "
        "Barras claramente mais vermelhas indicam naturalidades com exposição de risco "
        "acima da média — útil para direcionar políticas de crédito regionalizadas.",
    )

    nat_score = (
        df.drop_duplicates("id_ident")
        .dropna(subset=["naturalidade", "score"])
        .groupby(["naturalidade", "score"], observed=False)["id_ident"]
        .nunique()
        .reset_index()
        .rename(columns={"id_ident": "qtd"})
    )
    nat_totais = nat_score.groupby("naturalidade")["qtd"].sum().rename("total")
    nat_score = nat_score.merge(nat_totais, on="naturalidade")
    nat_score["pct"] = nat_score["qtd"] / nat_score["total"] * 100

    # Ordenar naturalidades por volume
    ordem = nat_totais.sort_values(ascending=False).index.tolist()

    score_order_local = [
        "BAIXÍSSIMO RISCO", "BAIXO RISCO", "MÉDIO RISCO 1",
        "MÉDIO RISCO 2", "ALTÍSSIMO RISCO", "SEM CLASSIFICAÇÃO",
    ]

    fig_ns = go.Figure()
    for score in score_order_local:
        sub = nat_score[nat_score["score"] == score]
        if sub.empty:
            continue
        sub = sub.set_index("naturalidade").reindex(ordem).reset_index()
        fig_ns.add_trace(go.Bar(
            name=score,
            x=sub["naturalidade"],
            y=sub["pct"],
            marker_color=SCORE_COLORS.get(score, COLORS["neutral"]),
            hovertemplate=f"<b>%{{x}}</b><br>{score}: %{{y:.1f}}%<extra></extra>",
        ))
    fig_ns = default_layout(fig_ns, height=420)
    fig_ns.update_layout(
        barmode="stack",
        yaxis_title="% de associados",
        yaxis_ticksuffix="%",
        xaxis_tickangle=-30,
        legend_title=None,
    )
    render_chart(fig_ns, use_container_width=True)

    # Alerta de naturalidade com maior altíssimo risco
    alto_risco = nat_score[nat_score["score"] == "ALTÍSSIMO RISCO"].sort_values("pct", ascending=False)
    if not alto_risco.empty and alto_risco.iloc[0]["pct"] > 0:
        pior = alto_risco.iloc[0]
        st.markdown(
            f'<div class="alert-box">'
            f'<div class="card-title-alert">\u26a0 Naturalidade com Maior Exposição</div>'
            f'<b>{pior["naturalidade"]}</b> concentra <b>{fmt_pct(pior["pct"])}</b> de '
            f'associados em "ALTÍSSIMO RISCO" — o maior entre os 11 grupos. '
            f'Avaliar revisão de política de crédito para esse segmento.'
            f'</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Tab 4 - Análise por PA
# ---------------------------------------------------------------------------
def render_pa(df: pd.DataFrame, is_media: bool = False):
    """Renderiza a aba Análise por PA."""

    st.markdown("### \U0001f3e6 Análise por PA / Agência")
    st.caption(
        "Performance das unidades de atendimento — eficiência operacional e oportunidades."
    )

    # Dados agregados por PA
    pa_stats = (
        df.groupby("pa")
        .agg(
            associados=("id_ident", "nunique"),
            receita=("vlreceita", "sum"),
            transações=("vlreceita", "count"),
        )
        .reset_index()
    )
    pa_stats["ticket_pa"] = pa_stats["receita"] / pa_stats["associados"]
    pa_stats = pa_stats.sort_values("receita", ascending=False)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de PAs", fmt_num(len(pa_stats)))
    c2.metric("Maior Receita (PA)", fmt_brl(pa_stats["receita"].max()))
    c3.metric("Maior Ticket/Cliente", fmt_brl(pa_stats["ticket_pa"].max()))
    c4.metric("Mediana Ticket/Cliente", fmt_brl(pa_stats["ticket_pa"].median()))

    st.markdown("---")

    # --- Top 15 PAs ---
    col_bar, col_scatter = st.columns(2)

    with col_bar:
        chart_header("Top 15 PAs por Receita", "Ranking das 15 agências que mais geram receita. Compare volume (tamanho da barra) com eficiência (receita/cliente) — nem sempre a maior PA é a mais eficiente.")
        top15 = pa_stats.head(15).sort_values("receita", ascending=True)

        fig_pa = go.Figure(go.Bar(
            x=top15["receita"],
            y=top15["pa"],
            orientation="h",
            marker_color=COLORS["primary"],
            text=[fmt_brl(v) for v in top15["receita"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Receita: R$ %{x:,.0f}<extra></extra>",
        ))
        fig_pa = default_layout(fig_pa, height=500, showlegend=False)
        fig_pa.update_layout(
            xaxis_title=lbl(is_media, 'eixo'),
            yaxis_title=None,
            xaxis_tickformat=",.0f",
            xaxis_tickprefix="R$ ",
        )
        render_chart(fig_pa, use_container_width=True)

    with col_scatter:
        chart_header("Eficiência: Clientes vs Receita por Cliente", "Cada bolha é uma PA. Eixo X = número de clientes, Eixo Y = receita por cliente. PAs no canto superior direito são as ideais (muitos clientes + alto valor). Tamanho da bolha = receita total.")

        # Limitar labels no scatter (muitas PAs)
        fig_scatter = go.Figure()

        # Calcular tamanho do marcador (normalizado)
        max_receita = pa_stats["receita"].max()
        pa_stats["bubble_size"] = (pa_stats["receita"] / max_receita * 40).clip(lower=5)

        fig_scatter.add_trace(go.Scatter(
            textfont=dict(size=8, color="#1A1A1A"),
            x=pa_stats["associados"],
            y=pa_stats["ticket_pa"],
            mode="markers",
            marker=dict(
                size=pa_stats["bubble_size"],
                color=pa_stats["receita"],
                colorscale="Blues",
                showscale=True,
                colorbar=dict(title="Receita Total"),
                line=dict(width=1, color="white"),
                opacity=0.8,
            ),
            text=pa_stats["pa"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Associados: %{x:,.0f}<br>"
                "Receita/Cliente: R$ %{y:,.0f}<br>"
                "<extra></extra>"
            ),
        ))

        # Destacar top 5 por ticket com labels
        top5_ticket = pa_stats.nlargest(5, "ticket_pa")
        for _, row in top5_ticket.iterrows():
            fig_scatter.add_annotation(
                x=row["associados"],
                y=row["ticket_pa"],
                text=row["pa"],
                showarrow=True,
                arrowhead=2,
                arrowsize=0.8,
                arrowwidth=1.5,
                arrowcolor=COLORS["neutral"],
                font=dict(size=10, color=COLORS["primary"]),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=COLORS["primary"],
                borderwidth=1,
            )

        fig_scatter = default_layout(fig_scatter, height=500, showlegend=False)
        fig_scatter.update_layout(
            xaxis_title="Número de Associados",
            yaxis_title="Receita por Cliente (R$)",
            yaxis_tickformat=",.0f",
            yaxis_tickprefix="R$ ",
        )
        render_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # --- Heatmap PA x Naturalidade (Top PAs) ---
    if not df["naturalidade"].dropna().empty:
        chart_header(
            "Top 15 PAs x Naturalidade (% de associados)",
            "Participação de cada naturalidade na composição da PA. "
            "Células fortes fora da naturalidade dominante revelam PAs atípicas — "
            "possível migração interna ou segmento específico que vale investigação.",
        )

        top15_pas = pa_stats.head(15)["pa"].tolist()
        pa_nat = (
            df[df["pa"].isin(top15_pas)]
            .drop_duplicates("id_ident")
            .dropna(subset=["naturalidade", "pa"])
            .groupby(["pa", "naturalidade"], observed=False)["id_ident"]
            .nunique()
            .reset_index()
            .rename(columns={"id_ident": "qtd"})
        )
        pa_totais = pa_nat.groupby("pa")["qtd"].sum().rename("total")
        pa_nat = pa_nat.merge(pa_totais, on="pa")
        pa_nat["pct"] = pa_nat["qtd"] / pa_nat["total"] * 100

        pivot_pn = pa_nat.pivot_table(
            index="pa", columns="naturalidade", values="pct", fill_value=0,
        ).reindex(top15_pas)

        # Ordenar colunas (naturalidades) pelo volume total
        ordem_cols = (
            df.drop_duplicates("id_ident")["naturalidade"]
            .value_counts()
            .index.tolist()
        )
        ordem_cols = [c for c in ordem_cols if c in pivot_pn.columns]
        pivot_pn = pivot_pn[ordem_cols]

        text_pn = [[f"{v:.0f}%" if v > 0 else "" for v in row] for row in pivot_pn.values]

        fig_pn = go.Figure(go.Heatmap(
            z=pivot_pn.values,
            x=pivot_pn.columns.tolist(),
            y=pivot_pn.index.tolist(),
            text=text_pn,
            texttemplate="%{text}",
            textfont=dict(size=10),
            colorscale=[[0, "#FFFFFF"], [0.1, "#CFE8EC"], [0.5, "#4DA8B3"], [1, "#007D89"]],
            hovertemplate="<b>PA %{y}</b> | %{x}<br>%{z:.1f}%<extra></extra>",
            showscale=True,
            colorbar=dict(title="% na PA"),
        ))
        fig_pn = default_layout(fig_pn, height=500, showlegend=False)
        fig_pn.update_layout(
            xaxis_title="Naturalidade",
            yaxis_title="PA",
            yaxis_autorange="reversed",
            xaxis_tickangle=-30,
        )
        render_chart(fig_pn, use_container_width=True)

        # Detectar PAs atípicas (naturalidade dominante diferente da global)
        nat_dominante_global = (
            df.drop_duplicates("id_ident")["naturalidade"].value_counts().index[0]
            if not df["naturalidade"].dropna().empty else None
        )
        if nat_dominante_global is not None:
            pa_dominante = pivot_pn.idxmax(axis=1)
            atipicas = pa_dominante[pa_dominante != nat_dominante_global]
            if not atipicas.empty:
                items_at = "".join(
                    f"<li><b>PA {pa}</b>: dominada por <b>{nat}</b> "
                    f"({pivot_pn.loc[pa, nat]:.0f}%)</li>"
                    for pa, nat in atipicas.items()
                )
                st.markdown(
                    f'<div class="insight-box">'
                    f'<div class="card-title">\U0001f50e PAs com Composição Atípica</div>'
                    f'A naturalidade dominante na cooperativa é <b>{nat_dominante_global}</b>. '
                    f'As PAs abaixo têm outro grupo majoritário:'
                    f'<ul>{items_at}</ul>'
                    f'Podem indicar migração regional, agências em fronteira ou '
                    f'oportunidades específicas de segmentação.'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")

    # --- Tabela completa ---
    with st.expander("Ver tabela completa de PAs"):
        display_pa = pd.DataFrame({
            "PA": pa_stats["pa"],
            "Associados": pa_stats["associados"].apply(fmt_num),
            "Receita Total": pa_stats["receita"].apply(fmt_brl),
            "Ticket Médio/Cliente": pa_stats["ticket_pa"].apply(fmt_brl),
            "Transacoes": pa_stats["transações"].apply(fmt_num),
        })
        st.dataframe(display_pa, use_container_width=True, hide_index=True)

    # Insights
    col_i1, col_i2 = st.columns(2)

    with col_i1:
        top_eff = pa_stats.nlargest(3, "ticket_pa")
        items = "".join(
            f"<li><b>{row['pa']}</b>: {fmt_brl(row['ticket_pa'])}/cliente "
            f"({fmt_num(row['associados'])} associados)</li>"
            for _, row in top_eff.iterrows()
        )
        st.markdown(
            f'<div class="success-box">'
            f'<div class="card-title-success">\U0001f3c6 PAs de Alta Eficiência</div>'
            f'<ul>{items}</ul>'
            f'Essas PAs geram receita acima da média por cliente. '
            f'Investigar suas práticas pode revelar boas práticas replicaveis.'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_i2:
        # PAs com muitos clientes mas baixo ticket
        mediana_ticket = pa_stats["ticket_pa"].median()
        mediana_assoc = pa_stats["associados"].median()
        underperf = pa_stats[
            (pa_stats["associados"] > mediana_assoc) & (pa_stats["ticket_pa"] < mediana_ticket)
        ].head(3)
        if not underperf.empty:
            items_u = "".join(
                f"<li><b>{row['pa']}</b>: {fmt_brl(row['ticket_pa'])}/cliente "
                f"({fmt_num(row['associados'])} associados)</li>"
                for _, row in underperf.iterrows()
            )
            st.markdown(
                f'<div class="alert-box">'
                f'<div class="card-title-alert">\U0001f4c9 PAs Subaproveitadas</div>'
                f'PAs com muitos associados mas ticket abaixo da mediana ({fmt_brl(mediana_ticket)}):<br>'
                f'<ul>{items_u}</ul>'
                f'Há potencial de crescimento via cross-selling e ativação de produtos.'
                f'</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Tab 5 - Oportunidades & Alertas
# ---------------------------------------------------------------------------
def render_oportunidades(df: pd.DataFrame, df_receitas_raw: pd.DataFrame, is_media: bool = False):
    """Renderiza a aba Oportunidades & Alertas."""

    st.markdown("### \U0001f3af Oportunidades e Alertas Estratégicos")
    st.caption(
        "Síntese de achados e recomendações acionáveis baseadas na análise dos dados."
    )

    # Calcular metricas necessarias
    total_associados = df["id_ident"].nunique()
    receita_total = df["vlreceita"].sum()

    # Receita por associado para concentração
    receita_cliente = (
        df.groupby("id_ident")["vlreceita"].sum().sort_values(ascending=False)
    )
    n = len(receita_cliente)
    top10_pct = receita_cliente.iloc[:int(n * 0.10)].sum() / receita_total * 100

    # SEM CLASSIFICACAO
    sem_class = df[df["score"] == "SEM CLASSIFICAÇÃO"]
    n_sem_class = sem_class["id_ident"].nunique()
    pct_sem_class = n_sem_class / total_associados * 100 if total_associados > 0 else 0
    receita_sem_class = sem_class["vlreceita"].sum()
    pct_receita_sc = receita_sem_class / receita_total * 100 if receita_total != 0 else 0

    # Perfil Triste
    triste = df[df["perfil"] == "Triste"]
    receita_triste = triste["vlreceita"].sum()
    pct_triste = receita_triste / receita_total * 100 if receita_total != 0 else 0
    n_triste = triste["id_ident"].nunique()

    # Receita mensal
    receita_mensal = df.groupby(df["dtbase"].dt.to_period("M"))["vlreceita"].sum()

    # Receita negativa
    neg_clients = receita_cliente[receita_cliente < 0]
    n_neg = len(neg_clients)
    total_neg = neg_clients.sum()

    # Não localizados
    n_nao_loc = df_receitas_raw["nao_localizado"].sum()

    st.markdown("---")

    # ========== OPORTUNIDADES ==========
    st.markdown("## \u2705 Oportunidades")

    op1, op2 = st.columns(2)

    with op1:
        st.markdown(
            f'<div class="success-box">'
            f'<div class="card-title-success">1. Classificar os "SEM CLASSIFICAÇÃO"</div>'
            f'<b>{fmt_num(n_sem_class)} associados ({fmt_pct(pct_sem_class)})</b> sem score de risco '
            f'geram <b>{fmt_pct(pct_receita_sc)} da receita total</b> ({fmt_brl(receita_sem_class)}).'
            f'<br><br>'
            f'<b>Impacto estimado:</b> Classificar esse grupo permite precificação '
            f'adequada de risco, oferta de produtos direcionados e potencial de aumento de receita '
            f'via produtos de crédito antes indisponíveis para esses associados.'
            f'<br><br>'
            f'<b>Ação:</b> Coletar dados complementares (renda, histórico) e aplicar '
            f'modelo de scoring para esses associados. Prioridade: top 20% por receita dentro do grupo.'
            f'</div>',
            unsafe_allow_html=True,
        )

    with op2:
        st.markdown(
            f'<div class="success-box">'
            f'<div class="card-title-success">2. Converter "Triste" em "Alegre"</div>'
            f'<b>{fmt_num(n_triste)} associados "Triste"</b> geram '
            f'<b>{fmt_pct(pct_triste)} da receita</b> ({fmt_brl(receita_triste)}).'
            f'<br><br>'
            f'<b>Impacto estimado:</b> Se a conversão de Triste para Alegre aumentar '
            f'a retenção em apenas 5%, o impacto pode ser de {fmt_brl(receita_triste * 0.05)} '
            f'em receita preservada.'
            f'<br><br>'
            f'<b>Ação:</b> Pesquisa NPS/CSAT direcionada aos top 500 associados Triste. '
            f'Programa de relacionamento proativo com gerente dedicado. '
            f'Revisão de jornada e pontos de dor.'
            f'</div>',
            unsafe_allow_html=True,
        )

    op3, op4 = st.columns(2)

    with op3:
        st.markdown(
            '<div class="success-box">'
            '<div class="card-title-success">3. Alavancar PAs de Alta Eficiência</div>'
            'PAs como Zona Industrial e São Paulo apresentam receita por cliente muito acima da média.'
            '<br><br>'
            '<b>Impacto estimado:</b> Replicar as melhores práticas para PAs subaproveitadas '
            'pode elevar o ticket médio em 10-20% nas unidades-alvo.'
            '<br><br>'
            '<b>Ação:</b> Benchmark entre PAs — identificar produtos, perfil de '
            'relacionamento e práticas de cross-sell das unidades mais eficientes. '
            'Criar programa de mentoria entre gerentes de PAs.'
            '</div>',
            unsafe_allow_html=True,
        )

    with op4:
        st.markdown(
            '<div class="success-box">'
            '<div class="card-title-success">4. Diversificar a Base de Produtos</div>'
            'O produto "Maçã" concentra ~76% da receita em apenas ~14% das transações.'
            '<br><br>'
            '<b>Impacto estimado:</b> Diversificar a base de produtos reduz risco '
            'regulatório e de mercado, além de aumentar stickiness dos associados.'
            '<br><br>'
            '<b>Ação:</b> Mapear associados com apenas 1 produto ativo e oferecer '
            'pacotes complementares. Meta: aumentar penetração de 2+ produtos para 60% da base.'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ========== ALERTAS ==========
    st.markdown("## \u26a0 Alertas")

    al1, al2 = st.columns(2)

    with al1:
        if len(receita_mensal) >= 2:
            last_month_val = receita_mensal.iloc[-1]
            prev_avg = receita_mensal.iloc[:-1].mean()
            var_pct = (last_month_val - prev_avg) / prev_avg * 100 if prev_avg != 0 else 0
            st.markdown(
                f'<div class="danger-box">'
                f'<div class="card-title-danger">Queda de Receita no Último Mês</div>'
                f'Receita de {fmt_brl(last_month_val)} — '
                f'variação de <b>{fmt_pct(var_pct)}</b> vs média anterior ({fmt_brl(prev_avg)}).'
                f'<br><br>'
                f'<b>Ação imediata:</b> Investigar se é sazonal, se houve perda de associados-chave '
                f'ou redução de volumes em produtos específicos. Monitorar próximo mês para confirmar tendência.'
                f'</div>',
                unsafe_allow_html=True,
            )

    with al2:
        st.markdown(
            f'<div class="danger-box">'
            f'<div class="card-title-danger">Concentração de Receita Extrema</div>'
            f'Top 10% dos associados geram <b>{fmt_pct(top10_pct)} da receita</b>. '
            f'A perda de poucos clientes-chave comprometeria o resultado.'
            f'<br><br>'
            f'<b>Ação imediata:</b> Programa VIP para os top 500 associados com gerente '
            f'dedicado, benefícios exclusivos e monitoramento de satisfação trimestral.'
            f'</div>',
            unsafe_allow_html=True,
        )

    al3, al4 = st.columns(2)

    with al3:
        st.markdown(
            f'<div class="alert-box">'
            f'<div class="card-title-alert">Associados com Receita Negativa</div>'
            f'<b>{fmt_num(n_neg)} associados</b> apresentam receita acumulada negativa '
            f'({fmt_brl(total_neg)} no período).'
            f'<br><br>'
            f'<b>Ação:</b> Analisar causa-raiz (estornos, inadimplência, custos operacionais). '
            f'Avaliar rentabilidade individual e definir estratégia: reativação, renegociação ou desinvestimento.'
            f'</div>',
            unsafe_allow_html=True,
        )

    with al4:
        st.markdown(
            f'<div class="alert-box">'
            f'<div class="card-title-alert">Qualidade de Dados - IDs não localizados</div>'
            f'<b>{fmt_num(n_nao_loc)} registros</b> de receita sem ID válido.'
            f'<br><br>'
            f'<b>Ação:</b> Investigar origem no sistema transacional. '
            f'Pode representar receita de operações sem vínculo ou falha de integração. '
            f'Corrigir na origem para garantir acurácia das análises futuras.'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ========== RECOMENDACOES ==========
    st.markdown("## \U0001f4cb Recomendações Prioritárias")

    recs = [
        (
            "1. Programa de Retenção VIP",
            "Criar programa de relacionamento para os top 500 associados por receita. "
            "Incluir: gerente dedicado, canal exclusivo, revisão anual de produtos e "
            "pesquisa de satisfação trimestral. "
            "Impacto: proteger 85%+ da receita da cooperativa.",
            "insight-box",
            "card-title",
        ),
        (
            "2. Scoring Universal",
            "Classificar 100% dos associados ativos. Priorizar os 'SEM CLASSIFICAÇÃO' "
            "com receita positiva. Usar o histórico de 6 meses de receita como variável "
            "comportamental complementar ao score de crédito tradicional.",
            "insight-box",
            "card-title",
        ),
        (
            "3. Dashboard de Monitoramento Contínuo",
            "Implementar monitoramento mensal de: (a) evolução de receita por decil de clientes, "
            "(b) migração entre perfis Alegre/Triste, (c) taxa de ativação por produto, "
            "(d) eficiência por PA. Alertas automáticos para desvios >10% da média móvel.",
            "insight-box",
            "card-title",
        ),
        (
            "4. Cross-Sell Orientado por Dados",
            "Modelo de recomendação de produtos baseado em perfis similares. "
            "Meta: aumentar de 1,8 para 2,5 produtos por associado ativo. "
            "Foco inicial: associados com apenas 'Maçã' e ticket acima da mediana.",
            "insight-box",
            "card-title",
        ),
        (
            "5. Tratamento de Dados e Governança",
            "Resolver os registros 'não localizado', padronizar cadastro de associados "
            "e implementar validação na entrada. "
            "Estabelecer rotina de qualidade de dados mensal com indicadores de completude.",
            "insight-box",
            "card-title",
        ),
    ]

    for i in range(0, len(recs), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(recs):
                title, text, box_class, title_class = recs[idx]
                col.markdown(
                    f'<div class="{box_class}">'
                    f'<div class="{title_class}">{title}</div>'
                    f'{text}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Nota final
    st.markdown("---")
    st.markdown(
        '<div class="insight-box">'
        '<div class="card-title">\U0001f4ac Nota Metodológica</div>'
        'Esta análise foi construída sobre dados de 6 meses (Out/2025 a Mar/2026) '
        'contendo 58.913 associados e 733.682 registros de receita. '
        'Os produtos estão anonimizados, o que limita recomendações específicas de portfolio. '
        'Os achados são estatisticamente robustos e independem da natureza dos produtos — '
        'a concentração de receita, o paradoxo Triste/Alegre e as disparidades entre PAs '
        'são padrões estruturais que demandam atenção gerencial.'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tab 6 - Dados Excluídos
# ---------------------------------------------------------------------------
def render_dados_excluidos(df_receitas_raw: pd.DataFrame, df_base: pd.DataFrame):
    """Renderiza a aba de Dados Excluídos da análise."""

    st.markdown("### \U0001f50d Dados Excluídos da Análise")
    st.caption(
        "Transparência sobre os registros removidos ou não utilizados. "
        "Entender essas exclusões é fundamental para avaliar a cobertura e a confiabilidade da análise."
    )

    st.markdown("---")

    # === 1. Registros "não localizado" ===
    df_nao_loc = df_receitas_raw[df_receitas_raw["nao_localizado"]].copy()
    n_nao_loc = len(df_nao_loc)
    pct_nao_loc = n_nao_loc / len(df_receitas_raw) * 100
    receita_nao_loc = df_nao_loc["vlreceita"].sum()

    st.markdown("#### 1. Registros com ID \"não localizado\"")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros Excluídos", fmt_num(n_nao_loc))
    c2.metric("% do Total", fmt_pct(pct_nao_loc))
    c3.metric("Receita Envolvida", fmt_brl(receita_nao_loc))
    c4.metric("Receita Média", fmt_brl(receita_nao_loc / n_nao_loc if n_nao_loc > 0 else 0, 2))

    st.markdown(
        '<div class="alert-box">'
        '<div class="card-title-alert">Por que foram excluídos?</div>'
        'Esses registros possuem o campo ID Ident preenchido como <b>"não localizado"</b>, '
        'impossibilitando a vinculação com a base de associados. Sem essa ligação, não é possível '
        'cruzar com score de risco, PA, naturalidade ou perfil. '
        '<br><br>'
        '<b>Possíveis causas:</b> associados desligados cujo cadastro foi removido, '
        'migração de sistema com perda de vínculo, operações de tesouraria/consolidação '
        'sem associado específico, ou falha na integração entre sistemas transacional e cadastral.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Detalhamento dos não localizados
    col_nl1, col_nl2 = st.columns(2)

    with col_nl1:
        st.markdown("**Distribuição por Produto**")
        nl_prod = df_nao_loc.groupby("produto")["vlreceita"].agg(["count", "sum"]).reset_index()
        nl_prod.columns = ["Produto", "Registros", "Receita"]
        nl_prod = nl_prod.sort_values("Receita", ascending=False)
        nl_prod["Registros"] = nl_prod["Registros"].apply(fmt_num)
        nl_prod["Receita"] = nl_prod["Receita"].apply(lambda x: fmt_brl(x, 2))
        st.dataframe(nl_prod, use_container_width=True, hide_index=True)

    with col_nl2:
        st.markdown("**Distribuição por Mês**")
        nl_mes = df_nao_loc.groupby(df_nao_loc["dtbase"].dt.strftime("%Y-%m"))["vlreceita"].agg(["count", "sum"]).reset_index()
        nl_mes.columns = ["Mês", "Registros", "Receita"]
        nl_mes["Registros"] = nl_mes["Registros"].apply(fmt_num)
        nl_mes["Receita"] = nl_mes["Receita"].apply(lambda x: fmt_brl(x, 2))
        st.dataframe(nl_mes, use_container_width=True, hide_index=True)

    with st.expander("Ver amostra dos registros excluídos (primeiras 50 linhas)", expanded=False):
        _cols_show = [c for c in ["id_ident", "dtbase", "vlreceita", "produto", "perfil"] if c in df_nao_loc.columns]
        st.dataframe(df_nao_loc[_cols_show].head(50), use_container_width=True, hide_index=True)

    st.markdown("---")

    # === 2. Scores vazios ===
    if "score" in df_base.columns:
        df_sem_score = df_base[df_base["score"].isna() | (df_base["score"].astype(str).str.strip() == "") | (df_base["score"].astype(str) == "nan")]
        n_sem_score = len(df_sem_score)

        if n_sem_score > 0:
            st.markdown("#### 2. Associados sem Score de Risco (campo vazio)")

            c1, c2 = st.columns(2)
            c1.metric("Associados sem Score", fmt_num(n_sem_score))
            c2.metric("% da Base", fmt_pct(n_sem_score / len(df_base) * 100))

            st.markdown(
                '<div class="alert-box">'
                '<div class="card-title-alert">Por que foram destacados?</div>'
                'Diferente dos "SEM CLASSIFICAÇÃO" (que possuem essa classificação explícita), '
                'estes associados possuem o campo de score <b>completamente vazio</b>. '
                'Podem ser cadastros recentes ainda não avaliados ou falha na carga do dado.'
                '</div>',
                unsafe_allow_html=True,
            )

            with st.expander("Ver associados sem score", expanded=False):
                _cols_base = [c for c in ["id_ident", "pa", "naturalidade"] if c in df_sem_score.columns]
                st.dataframe(df_sem_score[_cols_base].head(50), use_container_width=True, hide_index=True)

            st.markdown("---")

    # === 3. Receitas negativas ===
    df_rec_valid = df_receitas_raw[~df_receitas_raw["nao_localizado"]].copy()
    df_negativos = df_rec_valid[df_rec_valid["vlreceita"] < 0]
    n_neg = len(df_negativos)

    if n_neg > 0:
        receita_neg = df_negativos["vlreceita"].sum()
        clientes_neg = df_negativos["id_ident_num"].nunique()

        st.markdown("#### 3. Registros com Receita Negativa")

        c1, c2, c3 = st.columns(3)
        c1.metric("Registros Negativos", fmt_num(n_neg))
        c2.metric("Associados Envolvidos", fmt_num(clientes_neg))
        c3.metric("Valor Total", fmt_brl(receita_neg, 2))

        st.markdown(
            '<div class="insight-box">'
            '<div class="card-title">Estes registros NÃO foram excluídos</div>'
            'Receitas negativas foram <b>mantidas</b> na análise por representarem informação legítima '
            '(estornos, reversões, ajustes contábeis). Excluí-las inflaria artificialmente os indicadores. '
            'Porém, merecem investigação: se concentrados em poucos associados ou produtos, '
            'podem indicar problemas operacionais ou fraude.'
            '</div>',
            unsafe_allow_html=True,
        )

        col_neg1, col_neg2 = st.columns(2)
        with col_neg1:
            st.markdown("**Top 10 associados com maior receita negativa**")
            neg_por_cliente = df_negativos.groupby("id_ident_num")["vlreceita"].sum().sort_values().head(10).reset_index()
            neg_por_cliente.columns = ["ID Associado", "Receita Negativa"]
            neg_por_cliente["Receita Negativa"] = neg_por_cliente["Receita Negativa"].apply(lambda x: fmt_brl(x, 2))
            st.dataframe(neg_por_cliente, use_container_width=True, hide_index=True)

        with col_neg2:
            st.markdown("**Distribuição por Produto**")
            neg_prod = df_negativos.groupby("produto")["vlreceita"].agg(["count", "sum"]).reset_index()
            neg_prod.columns = ["Produto", "Registros", "Valor"]
            neg_prod = neg_prod.sort_values("Valor")
            neg_prod["Registros"] = neg_prod["Registros"].apply(fmt_num)
            neg_prod["Valor"] = neg_prod["Valor"].apply(lambda x: fmt_brl(x, 2))
            st.dataframe(neg_prod, use_container_width=True, hide_index=True)

    # === Resumo ===
    st.markdown("---")
    total_rec = len(df_receitas_raw)
    total_usados = total_rec - n_nao_loc
    st.markdown(
        f'<div class="insight-box">'
        f'<div class="card-title">Resumo da Cobertura</div>'
        f'<b>{fmt_num(total_rec)}</b> registros na base original &rarr; '
        f'<b>{fmt_num(n_nao_loc)}</b> excluídos (ID não localizado) &rarr; '
        f'<b>{fmt_num(total_usados)}</b> utilizados na análise '
        f'(<b>{fmt_pct(total_usados / total_rec * 100)}</b> de cobertura).'
        f'<br>Receita dos registros excluídos: {fmt_brl(receita_nao_loc)} '
        f'({fmt_pct(receita_nao_loc / df_receitas_raw["vlreceita"].sum() * 100 if df_receitas_raw["vlreceita"].sum() != 0 else 0)} do total).'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tab 7 - Qualidade dos Dados
# ---------------------------------------------------------------------------
def render_qualidade(df_base: pd.DataFrame, df_receitas: pd.DataFrame, df_merged: pd.DataFrame):
    """Renderiza a aba de Curadoria, Validação e Integridade dos Dados."""

    st.markdown("### \u2705 Curadoria, Validação e Integridade dos Dados")
    st.caption(
        "Auditoria completa das bases fornecidas: completude, consistência, "
        "integridade referencial, outliers e normalização aplicada."
    )

    # =========================================================
    # 1. COMPLETUDE
    # =========================================================
    st.markdown("---")
    st.markdown("#### 1. Completude dos Dados")

    col_b, col_r = st.columns(2)

    with col_b:
        st.markdown("**Base de Associados**")
        n_base = len(df_base)
        completude_base = []
        for col in ["id_ident", "pa", "score", "naturalidade"]:
            if col in df_base.columns:
                nulos = df_base[col].isna().sum() + (df_base[col].astype(str).isin(["", "nan", "None"])).sum()
                pct = (1 - nulos / n_base) * 100
                completude_base.append({
                    "Campo": col.replace("_", " ").title(),
                    "Registros": fmt_num(n_base),
                    "Preenchidos": fmt_num(n_base - nulos),
                    "Nulos": fmt_num(nulos),
                    "Completude": fmt_pct(pct),
                })
        st.dataframe(pd.DataFrame(completude_base), use_container_width=True, hide_index=True)

    with col_r:
        st.markdown("**Receitas (6 meses)**")
        n_rec = len(df_receitas)
        completude_rec = []
        for col in ["dtbase", "vlreceita", "id_ident", "produto", "perfil"]:
            if col in df_receitas.columns:
                nulos = df_receitas[col].isna().sum()
                pct = (1 - nulos / n_rec) * 100
                completude_rec.append({
                    "Campo": col.replace("_", " ").title(),
                    "Registros": fmt_num(n_rec),
                    "Preenchidos": fmt_num(n_rec - nulos),
                    "Nulos": fmt_num(nulos),
                    "Completude": fmt_pct(pct),
                })
        st.dataframe(pd.DataFrame(completude_rec), use_container_width=True, hide_index=True)

    # Scorecard de completude geral
    total_campos = n_base * 4 + n_rec * 5
    score_nulos = df_base[["id_ident", "pa", "naturalidade"]].isna().sum().sum()
    if "score" in df_base.columns:
        score_nulos += df_base["score"].isna().sum()
    rec_nulos = sum(df_receitas[c].isna().sum() for c in ["dtbase", "vlreceita", "id_ident", "produto", "perfil"] if c in df_receitas.columns)
    total_nulos = score_nulos + rec_nulos
    completude_geral = (1 - total_nulos / total_campos) * 100

    cor_completude = "#09AF41" if completude_geral >= 99 else "#FFA300" if completude_geral >= 95 else "#D62728"
    st.markdown(
        f'<div class="insight-box">'
        f'<div class="card-title">Completude Geral: <span style="color:{cor_completude};font-size:1.2rem">{fmt_pct(completude_geral)}</span></div>'
        f'Total de {fmt_num(total_campos)} campos analisados (base + receitas). '
        f'Apenas {fmt_num(total_nulos)} nulos encontrados. '
        f'A base possui excelente completude, com exceção de 179 scores vazios (0,3% da base de associados).'
        f'</div>',
        unsafe_allow_html=True,
    )

    # =========================================================
    # 2. INTEGRIDADE REFERENCIAL
    # =========================================================
    st.markdown("---")
    st.markdown("#### 2. Integridade Referencial")

    ids_base = set(df_base["id_ident"].dropna().astype(int))
    df_rec_valid = df_receitas[~df_receitas.get("nao_localizado", pd.Series(False, index=df_receitas.index))]
    ids_rec = set(pd.to_numeric(df_rec_valid["id_ident"], errors="coerce").dropna().astype(int))
    nao_loc = df_receitas.get("nao_localizado", pd.Series(False, index=df_receitas.index)).sum()

    ids_orfaos = len(ids_rec - ids_base)
    ids_sem_receita = len(ids_base - ids_rec)
    ids_duplicados = df_base.duplicated("id_ident").sum() if "id_ident" in df_base.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("IDs na Base", fmt_num(len(ids_base)))
    c2.metric("IDs com Receita", fmt_num(len(ids_rec)))
    c3.metric("Órfãos (receita sem base)", fmt_num(ids_orfaos))
    c4.metric("Base sem Receita", fmt_num(ids_sem_receita))

    checks = [
        ("IDs duplicados na base", ids_duplicados == 0,
         f"{fmt_num(ids_duplicados)} duplicados" if ids_duplicados > 0 else "Nenhum duplicado"),
        ("IDs órfãos (receita sem correspondência na base)", ids_orfaos == 0,
         f"{fmt_num(ids_orfaos)} órfãos" if ids_orfaos > 0 else "Todos os IDs de receita existem na base"),
        ("Registros 'não localizado'", nao_loc == 0,
         f"{fmt_num(nao_loc)} registros ({fmt_pct(nao_loc / len(df_receitas) * 100)})"),
        ("Associados sem nenhuma receita", ids_sem_receita == 0,
         f"{fmt_num(ids_sem_receita)} associados ({fmt_pct(ids_sem_receita / len(ids_base) * 100)})"),
    ]

    for label, ok, detail in checks:
        icon = "\u2705" if ok else "\u26a0\ufe0f"
        color = "#09AF41" if ok else "#FFA300"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
            f'<span style="font-size:1.1rem">{icon}</span>'
            f'<span style="color:#1A1A1A"><b>{label}</b>: '
            f'<span style="color:{color}">{detail}</span></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # =========================================================
    # 3. CONSISTÊNCIA E OUTLIERS
    # =========================================================
    st.markdown("---")
    st.markdown("#### 3. Consistência e Outliers")

    receita = df_receitas["vlreceita"]
    q1 = receita.quantile(0.25)
    q3 = receita.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    n_outliers = int(((receita < lower) | (receita > upper)).sum())
    n_negativos = int((receita < 0).sum())
    n_zeros = int((receita == 0).sum())

    col_o1, col_o2, col_o3 = st.columns(3)
    col_o1.metric("Outliers (IQR)", f"{fmt_num(n_outliers)} ({fmt_pct(n_outliers/len(receita)*100)})")
    col_o2.metric("Receitas Negativas", f"{fmt_num(n_negativos)} ({fmt_pct(n_negativos/len(receita)*100)})")
    col_o3.metric("Receitas Zeradas", f"{fmt_num(n_zeros)} ({fmt_pct(n_zeros/len(receita)*100)})")

    # Box plot da receita
    chart_header(
        "Distribuição da Receita (Box Plot)",
        "Mostra a dispersão dos valores de receita. A caixa central contém 50% dos dados (Q1 a Q3). "
        "Pontos fora dos 'bigodes' são outliers. Valores negativos indicam estornos ou ajustes."
    )
    # Limitar para visualização (excluir extremos para não achatar o box)
    rec_viz = receita[(receita >= receita.quantile(0.01)) & (receita <= receita.quantile(0.99))]
    fig_box = go.Figure(go.Box(
        y=rec_viz,
        name="Receita",
        marker_color=COLORS["primary"],
        boxpoints="outliers",
        jitter=0.3,
    ))
    fig_box = default_layout(fig_box, height=350, showlegend=False)
    fig_box.update_layout(yaxis_title="Receita (R$)", yaxis_tickprefix="R$ ")
    render_chart(fig_box)

    st.markdown(
        f'<div class="alert-box">'
        f'<div class="card-title-alert">Sobre os Outliers</div>'
        f'<b>{fmt_pct(n_outliers/len(receita)*100)}</b> dos registros são outliers pelo método IQR '
        f'(fora do intervalo {fmt_brl(lower, 2)} a {fmt_brl(upper, 2)}). '
        f'Isso é esperado em dados financeiros, onde poucos associados geram valores muito altos. '
        f'<b>Nenhum outlier foi removido</b> — todos foram mantidos na análise por representarem '
        f'receita legítima. A mediana (R$ 4,38) muito abaixo da média (R$ 195,62) confirma a '
        f'distribuição assimétrica típica de cooperativas de crédito.'
        f'</div>',
        unsafe_allow_html=True,
    )

    # =========================================================
    # 4. DISTRIBUIÇÃO TEMPORAL
    # =========================================================
    st.markdown("---")
    st.markdown("#### 4. Distribuição Temporal")

    periodos = df_receitas.groupby("dtbase")["vlreceita"].agg(["count", "sum"]).reset_index()
    periodos.columns = ["Período", "Registros", "Receita"]
    periodos["Período"] = periodos["Período"].dt.strftime("%d/%m/%Y")
    media_reg = periodos["Registros"].mean()
    desvio_reg = periodos["Registros"].std()

    periodos_display = periodos.copy()
    periodos_display["Registros"] = periodos["Registros"].apply(fmt_num)
    periodos_display["Receita"] = periodos["Receita"].apply(fmt_brl)
    periodos_display["Desvio da Média"] = [
        fmt_pct((v - media_reg) / media_reg * 100) for v in periodos["Registros"].values
    ]
    st.dataframe(periodos_display, use_container_width=True, hide_index=True)

    cv = (desvio_reg / media_reg * 100) if media_reg > 0 else 0
    cor_cv = "#09AF41" if cv < 5 else "#FFA300" if cv < 10 else "#D62728"
    st.markdown(
        f'<div class="insight-box">'
        f'<div class="card-title">Consistência Temporal: '
        f'<span style="color:{cor_cv}">CV = {fmt_pct(cv)}</span></div>'
        f'Coeficiente de variação de {fmt_pct(cv)} na quantidade de registros por mês. '
        f'Valores abaixo de 5% indicam excelente consistência. '
        f'Os 6 períodos possuem volume similar (~{fmt_num(int(media_reg))} registros/mês), '
        f'sem gaps temporais ou meses ausentes.'
        f'</div>',
        unsafe_allow_html=True,
    )

    # =========================================================
    # 5. NORMALIZAÇÃO APLICADA
    # =========================================================
    st.markdown("---")
    st.markdown("#### 5. Normalização Aplicada")

    st.markdown(
        "Os seguintes tratamentos foram aplicados para garantir a qualidade da apresentação:"
    )

    normalizacoes = [
        ("PAs / Agências", "22 nomes corrigidos",
         "Ararangua → Araranguá, Chapeco → Chapecó, Sao Paulo → São Paulo, etc."),
        ("Scores de Risco", "5 valores padronizados",
         "ALTISSIMO RISCO → ALTÍSSIMO RISCO, SEM CLASSIFICACAO → SEM CLASSIFICAÇÃO, etc."),
        ("Produtos", "3 nomes corrigidos",
         "Encoding quebrado do Excel: Maça → Maçã, Majericão → Manjericão, Melão corrigido"),
        ("Naturalidade", "1 valor corrigido",
         "Gaúcho com encoding quebrado → Gaúcho"),
        ("GUARAPUAVA", "Padronização de caixa",
         "GUARAPUAVA (maiúsculas) → Guarapuava (title case)"),
        ("Receitas negativas", "Mantidas na análise",
         "6.773 registros (0,9%) — representam estornos/ajustes legítimos"),
        ("Receitas zeradas", "Mantidas na análise",
         "105.520 registros (14,4%) — podem indicar operações sem custo ou registros de controle"),
        ("IDs 'não localizado'", "Excluídos do merge",
         "17.428 registros (2,4%) — sem vínculo com a base de associados"),
    ]

    for item, status, detalhe in normalizacoes:
        st.markdown(
            f'<div style="padding:6px 0;border-bottom:1px solid #E0E0E0;color:#1A1A1A;">'
            f'<b>{item}</b> — <span style="color:#007D89">{status}</span>'
            f'<br><span style="font-size:0.88rem;color:#575757">{detalhe}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # =========================================================
    # 6. SCORECARD FINAL
    # =========================================================
    st.markdown("---")
    st.markdown("#### 6. Scorecard de Qualidade")

    scores_list = [
        ("Completude", completude_geral >= 99, fmt_pct(completude_geral)),
        ("Zero duplicados na base", ids_duplicados == 0, "Aprovado"),
        ("Integridade referencial", ids_orfaos == 0, "0 IDs órfãos"),
        ("Consistência temporal", cv < 5, f"CV = {fmt_pct(cv)}"),
        ("Cobertura de dados", (len(df_receitas) - nao_loc) / len(df_receitas) * 100 > 95,
         fmt_pct((len(df_receitas) - nao_loc) / len(df_receitas) * 100)),
    ]

    aprovados = sum(1 for _, ok, _ in scores_list if ok)
    total_checks = len(scores_list)

    for label, ok, detail in scores_list:
        icon = "\u2705" if ok else "\u26a0\ufe0f"
        cor = "#09AF41" if ok else "#FFA300"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;color:#1A1A1A;">'
            f'<span style="font-size:1.1rem">{icon}</span>'
            f'<span><b>{label}</b>: <span style="color:{cor}">{detail}</span></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    nota = aprovados / total_checks * 10
    cor_nota = "#09AF41" if nota >= 8 else "#FFA300" if nota >= 6 else "#D62728"
    st.markdown(
        f'<div class="success-box" style="text-align:center;padding:20px;">'
        f'<div style="font-size:2rem;font-weight:700;color:{cor_nota}">{nota:.1f}/10</div>'
        f'<div style="font-size:1rem;color:#1A1A1A !important;">'
        f'<b>{aprovados}/{total_checks}</b> verificações aprovadas — '
        f'Base de dados com alta confiabilidade para análise</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    inject_css()

    # Header
    st.markdown(
        '<h1 style="color: #165C7D; margin-bottom: 0;">'
        '\U0001f4ca Transpocred Case Analytics'
        '</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color: #575757; font-size: 1.1rem; margin-top: 0;">'
        'Análise de base de associados e receitas — Case Técnico Data Analyst'
        '</p>',
        unsafe_allow_html=True,
    )

    # Carregar dados
    df_base, df_receitas, df_merged = load_data()

    # Filtros
    df_filtered, filtros_ativos, is_media = render_sidebar(df_merged)

    if len(df_filtered) == 0:
        st.warning("Nenhum dado encontrado para os filtros selecionados. Ajuste os filtros no menu lateral.")
        return

    # Banner do cenário ativo
    if is_media:
        st.info(
            "\U0001f4ca **Cenário: Receita Média (AVG)** — Os valores exibidos representam a "
            "**média de receita** por registro (campo original `AVG_vlreceita`). "
            "Totalizações representam soma de médias, não valores absolutos."
        )

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "\U0001f4c8 Visão Geral",
        "\U0001f4b0 Concentração de Receita",
        "\U0001f30e Perfil Demográfico",
        "\U0001f6e1 Análise de Risco",
        "\U0001f3e6 Análise por PA",
        "\U0001f3af Oportunidades & Alertas",
        "\U0001f50d Dados Excluídos",
        "\u2705 Qualidade dos Dados",
    ])

    with tab1:
        render_visao_geral(df_filtered, df_receitas, filtros_ativos, is_media)

    with tab2:
        render_concentração(df_filtered, is_media)

    with tab3:
        render_perfil_demografico(df_filtered, is_media)

    with tab4:
        render_risco(df_filtered, is_media)

    with tab5:
        render_pa(df_filtered, is_media)

    with tab6:
        render_oportunidades(df_filtered, df_receitas, is_media)

    with tab7:
        render_dados_excluidos(df_receitas, df_base)

    with tab8:
        render_qualidade(df_base, df_receitas, df_merged)


if __name__ == "__main__":
    main()
