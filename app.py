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

# ── Paleta ──────────────────────────────────────────────────────────────────
COR_FLEX   = "#2980B9"
COR_DIESEL = "#E67E22"
COR_HIBRIDO = "#27AE60"
MAPA_CORES = {"Flex": COR_FLEX, "Diesel": COR_DIESEL, "Híbrido": COR_HIBRIDO}

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
    df["rank_cm"] = df["consumo_medio"].rank(ascending=False).astype(int)
    df = df.sort_values("consumo_medio", ascending=False).reset_index(drop=True)
    return df

df = carregar_dados()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Brazil.svg/320px-Flag_of_Brazil.svg.png", width=80)
    st.title("Filtros")
    st.markdown("**Tipo de Combustível**")
    combustiveis = st.multiselect(
        "",
        options=df["combustivel"].unique().tolist(),
        default=df["combustivel"].unique().tolist(),
    )
    st.markdown("---")
    st.markdown("**Faixa de Preço (R$)**")
    preco_min, preco_max = int(df["preco"].min()), int(df["preco"].max())
    faixa = st.slider("", preco_min, preco_max, (preco_min, preco_max), step=5000,
                      format="R$ %d")
    st.markdown("---")
    st.markdown("**Ranking por**")
    ordenar_por = st.radio("", ["Consumo Médio (CM)", "Custo-Benefício (CB)"], index=0)
    st.markdown("---")
    st.caption("📊 Dados: INMETRO / PBE Veicular 2024")
    st.caption("🎓 TPAE II — Gabriel, Felype, Samuel")

# ── Aplicar filtros ─────────────────────────────────────────────────────────
col_ordem = "consumo_medio" if ordenar_por == "Consumo Médio (CM)" else "custo_beneficio"
df_filtrado = df[
    (df["combustivel"].isin(combustiveis)) &
    (df["preco"] >= faixa[0]) &
    (df["preco"] <= faixa[1])
].sort_values(col_ordem, ascending=False).reset_index(drop=True)

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.title("🚗 Avaliação da Relação Custo-Eficiência Energética")
st.markdown("**Veículos Leves Comercializados no Brasil** — Fonte: PBE Veicular 2024 (INMETRO)")
st.markdown("---")

# ── KPIs ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total de modelos", len(df_filtrado))
with k2:
    melhor_cm = df_filtrado.iloc[0]
    st.metric("Maior CM (km/L)", f"{melhor_cm['consumo_medio']:.2f}",
              help=melhor_cm["modelo"])
with k3:
    melhor_cb = df_filtrado.loc[df_filtrado["custo_beneficio"].idxmax()]
    st.metric("Maior CB (índice)", f"{melhor_cb['custo_beneficio']:.1f}",
              help=melhor_cb["modelo"])
with k4:
    preco_medio = df_filtrado["preco"].mean()
    st.metric("Preço médio", f"R$ {preco_medio:,.0f}".replace(",", "."))

st.markdown("---")

# ── Linha 1: Tabela + Pizza ──────────────────────────────────────────────────
col_tab, col_pie = st.columns([3, 2])

with col_tab:
    st.subheader("📋 Tabela de Ranking")
    tabela = df_filtrado[["modelo", "combustivel", "consumo_cidade",
                           "consumo_estrada", "consumo_medio",
                           "custo_beneficio", "preco"]].copy()
    tabela.index = range(1, len(tabela) + 1)
    tabela.columns = ["Modelo", "Combustível", "C. Cidade (km/L)",
                      "C. Estrada (km/L)", "CM (km/L)", "CB", "Preço (R$)"]
    tabela["Preço (R$)"] = tabela["Preço (R$)"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))

    def colorir_combustivel(val):
        cores = {"Flex": "#d6e9f8", "Diesel": "#fde9d2", "Híbrido": "#d5f5e3"}
        return f"background-color: {cores.get(val, '')}"

    st.dataframe(
        tabela.style.applymap(colorir_combustivel, subset=["Combustível"]),
        use_container_width=True,
        height=420,
    )

with col_pie:
    st.subheader("🔵 Distribuição por Combustível")
    contagem = df_filtrado["combustivel"].value_counts().reset_index()
    contagem.columns = ["Combustível", "Quantidade"]
    fig_pie = px.pie(
        contagem, names="Combustível", values="Quantidade",
        color="Combustível", color_discrete_map=MAPA_CORES,
        hole=0.4,
    )
    fig_pie.update_traces(textposition="outside", textinfo="percent+label",
                          textfont_size=13)
    fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20),
                          height=390)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ── Linha 2: Barras CM ──────────────────────────────────────────────────────
st.subheader("🏆 Top 5 — Maior Consumo Médio (km/L)")
top5_cm = df_filtrado.head(5)
fig_bar = px.bar(
    top5_cm,
    x="consumo_medio", y="modelo",
    orientation="h",
    color="combustivel",
    color_discrete_map=MAPA_CORES,
    text="consumo_medio",
    labels={"consumo_medio": "CM (km/L)", "modelo": "", "combustivel": "Combustível"},
)
fig_bar.update_traces(texttemplate="%{text:.2f} km/L", textposition="outside")
fig_bar.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis=dict(range=[0, top5_cm["consumo_medio"].max() * 1.2]),
    legend_title="Combustível",
    margin=dict(t=10, b=10),
    height=300,
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ── Linha 3: Dispersão CM × CB ──────────────────────────────────────────────
st.subheader("📈 Dispersão: Consumo Médio × Custo-Benefício")
st.caption("Ideal: alto CM (eixo X) e alto CB (eixo Y). Tamanho da bolha = preço.")
fig_scatter = px.scatter(
    df_filtrado,
    x="consumo_medio", y="custo_beneficio",
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
    margin=dict(t=20, b=20),
    height=480,
    legend_title="Combustível",
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ── Linha 4: Consumo urbano vs estrada por combustível ──────────────────────
st.subheader("🏙️ Consumo Médio: Urbano vs. Estrada por Tipo de Combustível")
media_comb = df_filtrado.groupby("combustivel")[["consumo_cidade", "consumo_estrada"]].mean().round(2).reset_index()
media_comb_long = media_comb.melt(id_vars="combustivel",
                                   value_vars=["consumo_cidade", "consumo_estrada"],
                                   var_name="Ciclo", value_name="km/L")
media_comb_long["Ciclo"] = media_comb_long["Ciclo"].map(
    {"consumo_cidade": "Urbano", "consumo_estrada": "Estrada"})

fig_group = px.bar(
    media_comb_long,
    x="combustivel", y="km/L", color="Ciclo",
    barmode="group",
    text="km/L",
    labels={"combustivel": "Combustível", "km/L": "Consumo médio (km/L)", "Ciclo": "Ciclo"},
    color_discrete_map={"Urbano": "#5DADE2", "Estrada": "#1A5276"},
)
fig_group.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig_group.update_layout(margin=dict(t=20, b=20), height=360)
st.plotly_chart(fig_group, use_container_width=True)

st.markdown("---")

# ── Rodapé ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; color:grey; font-size:12px;'>
    Gabriel Ackermann · Felype Dangel · Samuel Martins &nbsp;|&nbsp;
    TPAE II — UFPB &nbsp;|&nbsp; Dados: INMETRO / PBE Veicular 2024
    </div>
    """,
    unsafe_allow_html=True,
)
