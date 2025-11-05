import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Selic x IPCA x Juros Reais", layout="wide")

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

# Séries
selic_codigo = 432  # Selic Meta (% a.a.)
ipca_codigo = 433   # IPCA mensal (%)

# Períodos
periodos = [
    ("01/01/2015", "31/12/2019"),
    ("01/01/2020", datetime.today().strftime("%d/%m/%Y")),
]

# Selic Meta
selic_dfs = [get_bcb_data(selic_codigo, ini, fim) for ini, fim in periodos]
selic_df = pd.concat(selic_dfs, ignore_index=True)
selic_df["data"] = pd.to_datetime(selic_df["data"], dayfirst=True)
selic_df["valor"] = selic_df["valor"].astype(float)
selic_df = selic_df.sort_values("data")

# IPCA
ipca_dfs = [get_bcb_data(ipca_codigo, ini, fim) for ini, fim in periodos]
ipca_df = pd.concat(ipca_dfs, ignore_index=True)
ipca_df["data"] = pd.to_datetime(ipca_df["data"], dayfirst=True)
ipca_df["valor"] = ipca_df["valor"].astype(float)
ipca_df = ipca_df.sort_values("data")

# IPCA acumulado 12 meses
ipca_df["ipca_12m"] = ipca_df["valor"].rolling(12).sum()

# Interpolação IPCA para datas da Selic
ipca_interp = (
    ipca_df.set_index("data")["ipca_12m"]
    .reindex(selic_df["data"])
    .interpolate(method='time')
    .round(2)
    .reset_index()
)
ipca_interp.rename(columns={"index": "data"}, inplace=True)

# Juntar bases por data
df = selic_df.rename(columns={"valor": "selic"}).merge(ipca_interp, on="data")

# Juros reais
df["juros_reais"] = df["selic"] - df["ipca_12m"]

# Últimos valores
last_date = df["data"].max()
last_row = df.loc[df["data"] == last_date].iloc[0]

# Gráfico
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["data"], y=df["selic"].round(2),
    mode="lines", name="Selic (a.a.)", line=dict(color="blue")
))
fig.add_trace(go.Scatter(
    x=df["data"], y=df["ipca_12m"],
    mode="lines", name="IPCA 12m", line=dict(color="red")
))
fig.add_trace(go.Scatter(
    x=df["data"], y=df["juros_reais"],
    mode="lines", name="Juros Reais", line=dict(color="green")
))

fig.add_hline(y=0, line_dash="dot", line_color="black")

# Título centralizado
fig.update_layout(
    title=dict(
        text="<b>Selic x IPCA x Juros Reais</b>",
        x=0.5,  # centraliza
        xanchor="center",
        yanchor="top",
        font=dict(size=22)
    ),
    xaxis_title="Data",
    yaxis_title="Taxa (%)",
    hovermode="x unified",
    template="plotly_white"
)

# Marca d'água centralizada e semi-transparente
fig.add_layout_image(
    dict(
        source="Logo invest + XP preto.png",  # nome do arquivo da logo
        xref="paper", yref="paper",
        x=0.5, y=0.5,  # centro do gráfico
        sizex=0.9, sizey=0.9,  # tamanho relativo
        xanchor="center", yanchor="middle",
        opacity=0.15,  # transparência
        layer="below"  # atrás das linhas
    )
)

# Mostrar no Streamlit
st.plotly_chart(fig, use_container_width=True)
st.caption(f"Atualizado em: {last_date.strftime('%d/%m/%Y')}")
