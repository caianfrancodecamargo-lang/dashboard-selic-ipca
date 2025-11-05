import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st
import base64

st.set_page_config(page_title="Selic x IPCA x Juros Reais", layout="wide")

# ========== Funções ==========
@st.cache_data
def get_bcb_data(codigo_serie, start, end):
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados"
        f"?formato=json&dataInicial={start}&dataFinal={end}"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return pd.DataFrame(r.json())

# ========== Cores ==========
COLOR_SELIC = "#0B3D2E"      # Verde escuro Copaíba
COLOR_IPCA = "#6B8E23"       # Verde oliva
COLOR_JUROS = "#A4B787"      # Verde claro
COLOR_ZERO = "#333333"       # Cinza escuro

# ========== Séries ==========
selic_codigo = 432
ipca_codigo = 433

periodos = [
    ("01/01/2015", "31/12/2019"),
    ("01/01/2020", datetime.today().strftime("%d/%m/%Y")),
]

# ========== Dados Selic ==========
selic_dfs = [get_bcb_data(selic_codigo, ini, fim) for ini, fim in periodos]
selic_df = pd.concat(selic_dfs, ignore_index=True)
selic_df["data"] = pd.to_datetime(selic_df["data"], dayfirst=True)
selic_df["valor"] = selic_df["valor"].astype(float)
selic_df = selic_df.sort_values("data")

# ========== Dados IPCA ==========
ipca_dfs = [get_bcb_data(ipca_codigo, ini, fim) for ini, fim in periodos]
ipca_df = pd.concat(ipca_dfs, ignore_index=True)
ipca_df["data"] = pd.to_datetime(ipca_df["data"], dayfirst=True)
ipca_df["valor"] = ipca_df["valor"].astype(float)
ipca_df = ipca_df.sort_values("data")
ipca_df["ipca_12m"] = ipca_df["valor"].rolling(12).sum()

# Interpolar IPCA
ipca_interp = (
    ipca_df.set_index("data")["ipca_12m"]
    .reindex(selic_df["data"])
    .interpolate(method="time")
    .round(2)
    .reset_index()
)
ipca_interp.rename(columns={"index": "data"}, inplace=True)

# ========== Unir e calcular juros reais ==========
df = selic_df.rename(columns={"valor": "selic"}).merge(ipca_interp, on="data")
df["juros_reais"] = df["selic"] - df["ipca_12m"]

last_date = df["data"].max()

# ========== Gráfico ==========
fig = go.Figure()

# Marca d’água — ampliada e centralizada
with open("Logo invest + XP preto.png", "rb") as f:
    image_bytes = f.read()
    encoded_image = base64.b64encode(image_bytes).decode()

fig.add_layout_image(
    dict(
        source="data:image/png;base64," + encoded_image,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        sizex=1.6,  # Aumentado (antes 1.2)
        sizey=1.6,  # Aumentado (antes 1.2)
        xanchor="center", yanchor="middle",
        opacity=0.12,  # ligeiramente mais sutil
        layer="below"
    )
)

# Linhas principais
fig.add_trace(go.Scatter(
    x=df["data"], y=df["selic"],
    mode="lines", name="Selic (a.a.)",
    line=dict(color=COLOR_SELIC, width=2.8)
))
fig.add_trace(go.Scatter(
    x=df["data"], y=df["ipca_12m"],
    mode="lines", name="IPCA 12m",
    line=dict(color=COLOR_IPCA, width=2.8)
))
fig.add_trace(go.Scatter(
    x=df["data"], y=df["juros_reais"],
    mode="lines", name="Juros Reais",
    line=dict(color=COLOR_JUROS, width=2.8)
))

fig.add_hline(y=0, line_dash="dot", line_color=COLOR_ZERO)

# Layout com título centralizado visualmente
fig.update_layout(
    title=dict(
        text="<b>Selic x IPCA x Juros Reais</b>",
        x=0.5,
        xanchor="center",
        yanchor="top",
        font=dict(size=26, color="#0B3D2E")
    ),
    xaxis_title="Data",
    yaxis_title="Taxa (%)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(
        orientation="h",
        y=-0.2,
        x=0.5,
        xanchor="center",
        yanchor="top",
        font=dict(size=13)
    ),
    margin=dict(t=90, b=80, l=60, r=40),
)

# ========== Exibição no Streamlit ==========
st.plotly_chart(fig, use_container_width=True)
st.caption(f"Dados atualizados até {last_date.strftime('%d/%m/%Y')}")
