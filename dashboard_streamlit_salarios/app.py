import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# =========================
# 🎨 PALETA DE CORES
# =========================
AZUL_ESCURO = "#0B1C2D"
AZUL_SEC = "#021C33"
LARANJA = "#FF7300"
BRANCO = "#FFFFFF"

# =========================
# 🎯 CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard de Salários",
    page_icon="📊",
    layout="wide"
)

# =========================
# 🎨 CSS GLOBAL (SIDEBAR + FILTROS + KPIs)
# =========================
st.markdown("""
<style>
/* Fundo geral */

.stApp {
    background-color: #000000;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #000000;
}

/* Textos sidebar */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label {
    color: white;
}

/* Multiselect */
div[data-baseweb="select"] > div {
    background-color: #001969 !important;
    border-radius: 8px;
}

/* Tags selecionadas */
span[data-baseweb="tag"] {
    background-color: #001969 !important;
    color: white !important;
}

/* Botão X das tags */
span[data-baseweb="tag"] svg {
    color: white !important;
}

/* KPIs */
[data-testid="stMetricValue"] {
    color: #F57C00;
}

/* Divisores */
hr {
    border-color: #132A3E;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🎨 TEMA GLOBAL DO PLOTLY
# =========================
pio.templates["azul_laranja"] = dict(
    layout=dict(
        paper_bgcolor=AZUL_ESCURO,
        plot_bgcolor=AZUL_ESCURO,
        font=dict(color=BRANCO),
        title=dict(font=dict(color=BRANCO)),
        colorway=[LARANJA, "#011042"],
        xaxis=dict(gridcolor=AZUL_SEC, zerolinecolor=AZUL_SEC),
        yaxis=dict(gridcolor=AZUL_SEC, zerolinecolor=AZUL_SEC)
    )
)
pio.templates.default = "azul_laranja"

# =========================
# 📥 CARREGAMENTO DOS DADOS
# =========================
df = pd.read_csv(
    "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
)

# =========================
# 🔍 SIDEBAR – FILTROS
# =========================
st.sidebar.header("🔍 Filtros")

anos = sorted(df['ano'].unique())
anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)

senioridades = sorted(df['senioridade'].unique())
sen_sel = st.sidebar.multiselect("Senioridade", senioridades, default=senioridades)

contratos = sorted(df['contrato'].unique())
cont_sel = st.sidebar.multiselect("Tipo de Contrato", contratos, default=contratos)

tamanhos = sorted(df['tamanho_empresa'].unique())
tam_sel = st.sidebar.multiselect("Tamanho da Empresa", tamanhos, default=tamanhos)

# =========================
# 🧮 FILTRAGEM
# =========================
df_f = df[
    (df['ano'].isin(anos_sel)) &
    (df['senioridade'].isin(sen_sel)) &
    (df['contrato'].isin(cont_sel)) &
    (df['tamanho_empresa'].isin(tam_sel))
]

# =========================
# 🏷️ TÍTULO
# =========================
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados usando os filtros à esquerda.")

# =========================
# 📊 KPIs
# =========================
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_f.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Salário médio", f"${df_f['usd'].mean():,.0f}")
    c2.metric("Salário máximo", f"${df_f['usd'].max():,.0f}")
    c3.metric("Total de registros", f"{len(df_f):,}")
    c4.metric("Cargo mais frequente", df_f['cargo'].mode()[0])

st.markdown("---")

# =========================
# 📈 GRÁFICOS
# =========================
st.subheader("Gráficos")

g1, g2 = st.columns(2)

with g1:
    top = (
        df_f.groupby('cargo')['usd']
        .mean()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )
    fig = px.bar(
        top,
        x='usd',
        y='cargo',
        orientation='h',
        title="Top 10 cargos por salário médio",
        color_discrete_sequence=[LARANJA]
    )
    st.plotly_chart(fig, use_container_width=True)

with g2:
    fig = px.histogram(
        df_f,
        x='usd',
        nbins=30,
        title="Distribuição de salários",
        color_discrete_sequence=[LARANJA]
    )
    st.plotly_chart(fig, use_container_width=True)

g3, g4 = st.columns(2)

with g3:
    remoto = df_f['remoto'].value_counts().reset_index()
    remoto.columns = ['tipo', 'quantidade']
    fig = px.pie(
        remoto,
        names='tipo',
        values='quantidade',
        hole=0.5,
        title="Tipos de trabalho",
        color_discrete_sequence=[LARANJA, "#001969"]
    )
    st.plotly_chart(fig, use_container_width=True)

with g4:
    ds = df_f[df_f['cargo'] == 'Data Scientist']
    pais = ds.groupby('residencia_iso3')['usd'].mean().reset_index()
    fig = px.choropleth(
        pais,
        locations='residencia_iso3',
        color='usd',
        title="Salário médio de Data Scientist por país",
        color_continuous_scale=[AZUL_SEC, LARANJA]
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 📋 TABELA
# =========================
st.subheader("Dados Detalhados")
st.dataframe(df_f)
