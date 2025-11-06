import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st
import base64
from bs4 import BeautifulSoup

# ======================
# Configuração da página
# ======================
st.set_page_config(page_title="Selic x IPCA x Juros Reais", layout="wide")

# ======================
# Funções auxiliares
# ======================

@st.cache_data(ttl=86400)
def get_bcb_data(codigo_serie, start, end):
    """Busca séries do Banco Central (via SGS API)."""
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados"
        f"?formato=json&dataInicial={start}&dataFinal={end}"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return pd.DataFrame(r.json())

@st.cache_data(ttl=86400)
def get_copom_calendar():
    """Web scraping do calendário do Copom no site do Banco Central, com fallback."""
    url = "https://www.bcb.gov.br/publicacoes/atascopom/cronologicos"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        atas = soup.find_all("a", class_="link")

        dados = []
        for ata in atas:
            texto = ata.get_text(strip=True)
            if "Reunião" in texto and "de" in texto:
                try:
                    reuniao = texto.split("ª")[0] + "ª"
                    partes = texto.split("–")[1].strip().split(" de ")
                    if len(partes) >= 3:
                        dias = partes[0].replace("e", "-").strip()
                        mes = partes[1].strip()
                        ano = partes[2].strip()

                        inicio, fim = dias.split("-") if "-" in dias else (dias, dias)
                        inicio = f"{inicio.strip()} {mes} {ano}"
                        fim = f"{fim.strip()} {mes} {ano}"

                        # Converter mês em português (ex: julho) para número
                        meses = {
                            "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
                            "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
                            "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
                        }
                        mes_num = meses.get(mes.lower(), 1)

                        inicio_dt = datetime(int(ano), mes_num, int(inicio.split()[0]))
                        fim_dt = datetime(int(ano), mes_num, int(fim.split()[0]))

                        dados.append({"reuniao": reuniao, "inicio": inicio_dt, "fim": fim_dt})
                except Exception:
                    continue

        if not dados:
            raise ValueError("Nenhum dado encontrado.")

        df = pd.DataFrame(dados).sort_values("fim", ascending=True).reset_index(drop=True)
        return df

    except Exception as e:
        st.warning(f"⚠️ Falha ao obter dados do site do Banco Central ({e}). Usando calendário padrão.")

        dados_padrao = [
            {"reuniao": "267ª", "inicio": datetime(2024, 1, 30), "fim": datetime(2024, 1, 31)},
            {"reuniao": "268ª", "inicio": datetime(2024, 3, 19), "fim": datetime(2024, 3, 20)},
            {"reuniao": "269ª", "inicio": datetime(2024, 5, 7), "fim": datetime(2024, 5, 8)},
            {"reuniao": "270ª", "inicio": datetime(2024, 6, 18), "fim": datetime(2024, 6, 19)},
            {"reuniao": "271ª", "inicio": datetime(2024, 7, 30), "fim": datetime(2024, 7, 31)},
            {"reuniao": "272ª", "inicio": datetime(2024, 9, 17), "fim": datetime(2024, 9, 18)},
            {"reuniao": "273ª", "inicio": datetime(2024, 10, 29), "fim": datetime(2024, 10, 30)},
            {"reuniao": "274ª", "inicio": datetime(2024, 12, 17), "fim": datetime(2024, 12, 18)},
        ]
        return pd.DataFrame(dados_padrao)

# ======================
# Cores
# ======================
COLOR_SELIC = "#0B3D2E"
COLOR_IPCA = "#6B8E23"
COLOR_JUROS = "#4FA3A3"
COLOR_ZERO = "#333333"

# ======================
# Séries e períodos
# ======================
selic_codigo = 432
ipca_codigo = 433
periodos = [
    ("01/01/2015", "31/12/2019"),
    ("01/01/2020", datetime.today().strftime("%d/%m/%Y")),
]

# ======================
# Dados Selic
# ======================
selic_dfs = [get_bcb_data(selic_codigo, ini, fim) for ini, fim in periodos]
selic_df = pd.concat(selic_dfs, ignore_index=True)
selic_df["data"] = pd.to_datetime(selic_df["data"], dayfirst=True)
selic_df["valor"] = selic_df["valor"].astype(float)
selic_df = selic_df.sort_values("data")

# ======================
# Dados IPCA (composto)
# ======================
ipca_dfs = [get_bcb_data(ipca_codigo, ini, fim) for ini, fim in periodos]
ipca_df = pd.concat(ipca_dfs, ignore_index=True)
ipca_df["data"] = pd.to_datetime(ipca_df["data"], dayfirst=True)
ipca_df["valor"] = ipca_df["valor"].astype(float)
ipca_df = ipca_df.sort_values("data")
ipca_df["fator"] = 1 + (ipca_df["valor"] / 100)
ipca_df["ipca_12m"] = (ipca_df["fator"].rolling(12).apply(lambda x: x.prod(), raw=True) - 1) * 100

ipca_interp = (
    ipca_df.set_index("data")["ipca_12m"]
    .reindex(selic_df["data"])
    .interpolate(method="time")
    .round(2)
    .reset_index()
)

df = selic_df.rename(columns={"valor": "selic"}).merge(ipca_interp, on="data")
df["juros_reais"] = df["selic"] - df["ipca_12m"]
last_date = df["data"].max()

# ======================
# Dados do Copom
# ======================
copom_df = get_copom_calendar()

# ======================
# Gráfico
# ======================
fig = go.Figure()

# Marca d’água
try:
    with open("Logo invest + XP preto.png", "rb") as f:
        image_bytes = f.read()
        encoded_image = base64.b64encode(image_bytes).decode()
    fig.add_layout_image(
        dict(
            source="data:image/png;base64," + encoded_image,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=2.3, sizey=2.3,
            xanchor="center", yanchor="middle",
            opacity=0.12,
            layer="below"
        )
    )
except:
    pass

# Linhas principais
fig.add_trace(go.Scatter(x=df["data"], y=df["selic"], mode="lines", name="Selic (a.a.)",
                         line=dict(color=COLOR_SELIC, width=2.5)))
fig.add_trace(go.Scatter(x=df["data"], y=df["ipca_12m"], mode="lines", name="IPCA 12m",
                         line=dict(color=COLOR_IPCA, width=2.5)))
fig.add_trace(go.Scatter(x=df["data"], y=df["juros_reais"], mode="lines", name="Juros Reais",
                         line=dict(color=COLOR_JUROS, width=2.5)))

# Linhas verticais: reuniões do Copom
for _, row in copom_df.iterrows():
    fig.add_vrect(
        x0=row["inicio"], x1=row["fim"],
        fillcolor="rgba(11, 61, 46, 0.05)",
        line_width=0,
        annotation_text=row["reuniao"],
        annotation_position="top left",
        annotation_font_size=10
    )

fig.add_hline(y=0, line_dash="dot", line_color=COLOR_ZERO)

fig.update_layout(
    title=dict(
        text="<b>Selic x IPCA x Juros Reais</b>",
        x=0.5, y=0.98,
        font=dict(size=26, color="#0B3D2E"),
        xanchor="center", yanchor="top"
    ),
    xaxis_title="Data",
    yaxis_title="Taxa (%)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top"),
    margin=dict(t=120, b=50, l=50, r=50),
)

# ======================
# Exibição no Streamlit
# ======================
st.plotly_chart(fig, use_container_width=True)
st.caption(f"Dados atualizados até {last_date.strftime('%d/%m/%Y')}")

# Mostrar calendário Copom abaixo do gráfico
st.subheader("📅 Próximas reuniões do Copom")
st.dataframe(copom_df)
