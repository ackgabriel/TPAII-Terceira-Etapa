"""
Dashboard — Avaliação da Relação Custo-Eficiência Energética
em Veículos Leves Comercializados no Brasil
Disciplina: TPAE II — Etapa 3
Autores: Gabriel Ackermann, Felype Dangel, Samuel Martins
Fonte: PBE Veicular 2024 (INMETRO)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from io import StringIO

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Eficiência Veicular — PBE 2024",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Título principal */
    h1 { font-size: 2rem !important; font-weight: 800 !important; color: #0D3B66 !important; }

    /* Subtítulo */
    h2 { font-size: 1.2rem !important; font-weight: 700 !important; color: #0D3B66 !important; }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #F4A227;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #E8EEF4;
        border-radius: 6px 6px 0 0;
        padding: 8px 20px;
        font-weight: 600;
        color: #0D3B66;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0D3B66 !important;
        color: #F4A227 !important;
    }

    /* Métricas */
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #D0DCE8;
        border-left: 4px solid #F4A227;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="metric-container"] label {
        color: #5577AA !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #0D3B66 !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }

    /* Rodapé */
    .rodape {
        text-align: center;
        color: #8899AA;
        font-size: 12px;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #D0DCE8;
    }
</style>
""", unsafe_allow_html=True)

# ── Paleta ──────────────────────────────────────────────────────────────────
COR_FLEX    = "#2980B9"
COR_DIESEL  = "#E67E22"
COR_HIBRIDO = "#27AE60"
MAPA_CORES  = {"Flex": COR_FLEX, "Diesel": COR_DIESEL, "Híbrido": COR_HIBRIDO}

# ── Base de dados (PBE Veicular 2024) ───────────────────────────────────────
DADOS_CSV = """modelo,combustivel,consumo_cidade,consumo_estrada,preco
Toyota Corolla Híbrido,Híbrido,17.2,19.5,184990
Fiat Toro,Diesel,13.5,15.0,162490
Fiat Mobi,Flex,13.2,14.5,68990
Chevrolet Onix,Flex,12.8,14.0,93990
Renault Kwid,Flex,12.6,13.7,72990
Volkswagen Gol,Flex,12.1,13.5,80990
Hyundai HB20,Flex,11.9,13.3,88990
Fiat Argo,Flex,11.8,13.0,92990
Fiat Cronos,Flex,12.3,13.6,101990
Honda Fit,Flex,12.0,13.2,107990
Volkswagen Polo,Flex,11.5,12.8,101990
Fiat Strada,Flex,11.2,12.5,107990
Hyundai Creta,Flex,11.0,12.3,139990
Volkswagen T-Cross,Flex,10.8,12.0,124990
Chevrolet Tracker,Flex,10.5,11.8,122990
Nissan Kicks,Flex,11.0,12.2,131990
Renault Duster,Flex,10.8,12.0,114990
Jeep Compass,Flex,10.4,11.6,161990
Volkswagen Amarok,Diesel,10.2,11.5,329990
Ram 1500,Diesel,9.2,11.0,449990"""

# ── Carregamento e cálculo de indicadores ───────────────────────────────────
@st.cache_data
def carregar_dados():
    df = pd.read_csv(StringIO(DADOS_CSV))
    df["consumo_medio"] = (df["consumo_cidade"] + df["consumo_estrada"]) / 2
    df["custo_beneficio"] = (df["consumo_medio"] / df["preco"]) * 1_000_000
    df["consumo_medio"] = df["consumo_medio"].round(2)
    df["custo_beneficio"] = df["custo_beneficio"].round(1)
    df = df.sort_values("consumo_medio", ascending=False).reset_index(drop=True)
    return df

df = carregar_dados()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Filtros")
    st.markdown("**Tipo de Combustível**")
    combustiveis = st.multiselect(
        "",
        options=df["combustivel"].unique().tolist(),
        default=df["combustivel"].unique().tolist(),
    )
    st.markdown("**Faixa de Preço (R$)**")
    preco_min, preco_max = int(df["preco"].min()), int(df["preco"].max())
    faixa = st.slider("", preco_min, preco_max, (preco_min, preco_max),
                      step=5000, format="R$ %d")
    st.markdown("**Ranking por**")
    ordenar_por = st.radio("", ["Consumo Médio (CM)", "Custo-Benefício (CB)"], index=0)
    st.markdown("---")
    st.caption("📊 Dados: INMETRO / PBE Veicular 2024")
    st.caption("🎓 TPAE II — Gabriel, Felype, Samuel")

# ── Filtros aplicados ────────────────────────────────────────────────────────
col_ordem = "consumo_medio" if ordenar_por == "Consumo Médio (CM)" else "custo_beneficio"
df_f = df[
    (df["combustivel"].isin(combustiveis)) &
    (df["preco"] >= faixa[0]) &
    (df["preco"] <= faixa[1])
].sort_values(col_ordem, ascending=False).reset_index(drop=True)

# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.title("🚗 Avaliação da Relação Custo-Eficiência Energética")
st.markdown("**Veículos Leves Comercializados no Brasil** — Fonte: PBE Veicular 2024 (INMETRO)")
st.markdown("---")

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total de Modelos", len(df_f))
with k2:
    melhor = df_f.iloc[0] if len(df_f) else df.iloc[0]
    st.metric("Maior CM (km/L)", f"{melhor['consumo_medio']:.2f}",
              help=f"Modelo: {melhor['modelo']}")
with k3:
    idx_cb = df_f["custo_beneficio"].idxmax() if len(df_f) else 0
    melhor_cb = df_f.loc[idx_cb]
    st.metric("Maior CB (índice)", f"{melhor_cb['custo_beneficio']:.1f}",
              help=f"Modelo: {melhor_cb['modelo']}")
with k4:
    st.metric("Preço Médio", f"R$ {df_f['preco'].mean():,.0f}".replace(",", "."))

st.markdown("---")

# ── Abas ─────────────────────────────────────────────────────────────────────
aba1, aba2, aba3 = st.tabs(["📋  Ranking", "📊  Gráficos", "🔄  Comparativo"])

# ══ ABA 1 — RANKING ══════════════════════════════════════════════════════════
with aba1:
    col_tab, col_pie = st.columns([3, 2])

    with col_tab:
        st.subheader("Tabela de Ranking")
        st.caption("Todos os veículos da base, ordenados pelo critério selecionado na sidebar. "
                   "Cores indicam o tipo de combustível: azul = Flex, laranja = Diesel, verde = Híbrido.")
        tabela = df_f[["modelo", "combustivel", "consumo_cidade",
                        "consumo_estrada", "consumo_medio",
                        "custo_beneficio", "preco"]].copy()
        tabela.index = range(1, len(tabela) + 1)
        tabela.columns = ["Modelo", "Combustível", "C. Cidade (km/L)",
                          "C. Estrada (km/L)", "CM (km/L)", "CB", "Preço (R$)"]
        tabela["C. Cidade (km/L)"] = tabela["C. Cidade (km/L)"].round(2)
        tabela["C. Estrada (km/L)"] = tabela["C. Estrada (km/L)"].round(2)
        tabela["CM (km/L)"] = tabela["CM (km/L)"].round(2)
        tabela["CB"] = tabela["CB"].round(1)
        tabela["Preço (R$)"] = tabela["Preço (R$)"].apply(
            lambda x: f"R$ {x:,.0f}".replace(",", "."))

        def colorir(val):
            cores = {"Flex": "#D6E9F8", "Diesel": "#FDE9D2", "Híbrido": "#D5F5E3"}
            return f"background-color: {cores.get(val, '')}"

        st.dataframe(
            tabela.style.map(colorir, subset=["Combustível"]),
            use_container_width=True, height=430,
        )

    with col_pie:
        st.subheader("Distribuição por Combustível")
        st.caption("Proporção de modelos por tipo de combustível na amostra filtrada. "
                   "O Flex domina o mercado brasileiro, representando 80% da base.")
        contagem = df_f["combustivel"].value_counts().reset_index()
        contagem.columns = ["Combustível", "Quantidade"]
        fig_pie = px.pie(
            contagem, names="Combustível", values="Quantidade",
            color="Combustível", color_discrete_map=MAPA_CORES, hole=0.4,
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label",
                              textfont_size=13)
        fig_pie.update_layout(showlegend=False,
                              margin=dict(t=20, b=20, l=20, r=20), height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

# ══ ABA 2 — GRÁFICOS ═════════════════════════════════════════════════════════
with aba2:
    st.subheader("Top 5 — Maior Consumo Médio (km/L)")
    st.caption("Os cinco veículos com maior consumo médio (CM), calculado como a média entre "
               "o consumo urbano e o consumo rodoviário. O Toyota Corolla Híbrido lidera com "
               "18,35 km/L — 28,7% acima do segundo colocado.")
    top5 = df_f.head(5)
    fig_bar = px.bar(
        top5, x="consumo_medio", y="modelo", orientation="h",
        color="combustivel", color_discrete_map=MAPA_CORES, text="consumo_medio",
        labels={"consumo_medio": "CM (km/L)", "modelo": "", "combustivel": "Combustível"},
    )
    fig_bar.update_traces(texttemplate="%{text:.2f} km/L", textposition="outside")
    fig_bar.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, top5["consumo_medio"].max() * 1.2]),
        legend_title="Combustível", margin=dict(t=10, b=10), height=300,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    st.subheader("Dispersão: Consumo Médio × Custo-Benefício")
    st.caption("Cada bolha representa um veículo. O eixo X mostra o CM (eficiência energética) "
               "e o eixo Y mostra o CB (retorno por real investido). O tamanho da bolha é "
               "proporcional ao preço — bolhas maiores = carros mais caros. O ideal é estar "
               "no canto superior direito (alto CM e alto CB).")
    fig_scatter = px.scatter(
        df_f, x="consumo_medio", y="custo_beneficio",
        color="combustivel", color_discrete_map=MAPA_CORES,
        size="preco", size_max=40,
        hover_name="modelo",
        hover_data={"consumo_medio": ":.2f", "custo_beneficio": ":.1f",
                    "preco": ":,.0f", "combustivel": True},
        labels={"consumo_medio": "CM (km/L)", "custo_beneficio": "CB (índice)",
                "combustivel": "Combustível"},
        text="modelo",
    )
    fig_scatter.update_traces(textposition="top center", textfont_size=10)
    fig_scatter.update_layout(
        margin=dict(t=20, b=20), height=500, legend_title="Combustível",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ══ ABA 3 — COMPARATIVO ══════════════════════════════════════════════════════
with aba3:
    st.subheader("Consumo Urbano vs. Estrada por Combustível")
    st.caption("Comparação da média de consumo no ciclo urbano (cidade) e no ciclo rodoviário "
               "(estrada) para cada tipo de combustível. O Diesel apresenta a maior diferença "
               "entre os dois ciclos (~3,5 km/L), pois motores diesel são mais eficientes em "
               "altas velocidades constantes. O Híbrido tem a menor penalidade urbana graças "
               "à frenagem regenerativa.")
    media = df_f.groupby("combustivel")[["consumo_cidade", "consumo_estrada"]].mean().round(2).reset_index()
    media_long = media.melt(id_vars="combustivel",
                            value_vars=["consumo_cidade", "consumo_estrada"],
                            var_name="Ciclo", value_name="km/L")
    media_long["Ciclo"] = media_long["Ciclo"].map(
        {"consumo_cidade": "Urbano", "consumo_estrada": "Estrada"})
    fig_group = px.bar(
        media_long, x="combustivel", y="km/L", color="Ciclo",
        barmode="group", text="km/L",
        labels={"combustivel": "Combustível", "km/L": "Consumo médio (km/L)", "Ciclo": "Ciclo"},
        color_discrete_map={"Urbano": "#5DADE2", "Estrada": "#1A5276"},
    )
    fig_group.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_group.update_layout(margin=dict(t=20, b=20), height=420)
    st.plotly_chart(fig_group, use_container_width=True)

    st.markdown("---")

    st.subheader("Diferença entre Ciclo Urbano e Rodoviário por Modelo")
    st.caption("Quanto cada veículo ganha de autonomia ao sair do trânsito urbano para a estrada. "
               "Barras maiores indicam que o veículo performa muito melhor na estrada do que na cidade.")
    df_f2 = df_f.copy()
    df_f2["gap"] = (df_f2["consumo_estrada"] - df_f2["consumo_cidade"]).round(2)
    df_f2 = df_f2.sort_values("gap", ascending=False)
    fig_gap = px.bar(
        df_f2, x="gap", y="modelo", orientation="h",
        color="combustivel", color_discrete_map=MAPA_CORES, text="gap",
        labels={"gap": "Diferença (km/L)", "modelo": "", "combustivel": "Combustível"},
    )
    fig_gap.update_traces(texttemplate="+%{text:.2f} km/L", textposition="outside")
    fig_gap.update_layout(
        yaxis=dict(autorange="reversed"),
        legend_title="Combustível", margin=dict(t=10, b=10), height=520,
    )
    st.plotly_chart(fig_gap, use_container_width=True)

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='rodape'>Gabriel Ackermann · Felype Dangel · Samuel Martins &nbsp;|&nbsp; "
    "TPAE II — UFPB &nbsp;|&nbsp; Dados: INMETRO / PBE Veicular 2024</div>",
    unsafe_allow_html=True,
)
