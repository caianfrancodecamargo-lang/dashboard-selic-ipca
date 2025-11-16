# -*- coding: utf-8 -*-
import streamlit as st
import urllib.request
import gzip
import json
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
import numpy as np
import re
from datetime import datetime, timedelta
import base64

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Fundos de Investimentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para converter imagem local em base64
def get_image_base64(image_path):
    """Converte uma imagem local para base64 para uso no Plotly"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Caminho da logo
LOGO_PATH = "copaiba_logo.png"
logo_base64 = get_image_base64(LOGO_PATH)

# CSS customizado com espaçamentos reduzidos na sidebar
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Variáveis de cores inspiradas no Copaíba */
    :root {
        --primary-color: #1a5f3f;
        --secondary-color: #2d8659;
        --accent-color: #f0b429;
        --dark-bg: #0f1419;
        --light-bg: #f8f9fa;
        --text-dark: #1a1a1a;
        --text-light: #ffffff;
    }

    /* Fundo geral */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar com padding reduzido */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6b9b7f 0%, #8ba888 100%);
        padding: 1rem 0.8rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Logo na sidebar - espaçamento reduzido */
    [data-testid="stSidebar"] .sidebar-logo {
        text-align: center;
        padding: 0.5rem 0 0.8rem 0 !important;
        margin-bottom: 0.8rem !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }

    [data-testid="stSidebar"] .sidebar-logo img {
        max-width: 240px !important;
        height: auto;
        filter: brightness(1.1);
    }

    /* Labels dos inputs - espaçamento reduzido */
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.8rem !important;
        margin-bottom: 0.2rem !important;
        margin-top: 0 !important;
    }

    /* Reduzir espaçamento entre elementos */
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.4rem !important;
    }

    /* Título "Período de Análise" com menos espaço */
    [data-testid="stSidebar"] h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
        font-size: 0.85rem !important;
    }

    /* Divisores com menos espaço */
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
    }

    /* INPUTS COM BORDA ELEGANTE */
    [data-testid="stSidebar"] input {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.6) !important;
        color: #000000 !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.3s ease !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stSidebar"] input::placeholder {
        color: #666666 !important;
        opacity: 0.8 !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] input:focus {
        color: #000000 !important;
        border-color: #8ba888 !important;
        box-shadow: 0 4px 12px rgba(139, 168, 136, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stSidebar"] input:hover {
        border-color: rgba(139, 168, 136, 0.5) !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12) !important;
    }

    /* BOTÃO COM DEGRADÊ - espaçamento reduzido */
    .stButton > button {
        background: linear-gradient(135deg, #6b9b7f 0%, #8ba888 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 3px 12px rgba(107, 155, 127, 0.3) !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-top: 0.5rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 16px rgba(107, 155, 127, 0.5) !important;
        background: linear-gradient(135deg, #8ba888 0%, #6b9b7f 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Mensagens de validação - espaçamento reduzido */
    [data-testid="stSidebar"] .stAlert {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%) !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.7rem !important;
        margin: 0.3rem 0 !important;
        border-left: 3px solid #28a745 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        font-size: 0.8rem !important;
    }

    [data-testid="stSidebar"] .stAlert [data-testid="stMarkdownContainer"] {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Título principal */
    h1 {
        color: #1a5f3f;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Cards de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a5f3f;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f6f1 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #6b9b7f;
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #ffffff 0%, #f8f6f1 100%);
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #6c757d;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(107, 155, 127, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6b9b7f 0%, #8ba888 100%);
        color: white !important;
        box-shadow: 0 3px 10px rgba(107, 155, 127, 0.3);
    }

    /* Subtítulos */
    h2, h3 {
        color: #1a5f3f;
        font-weight: 600;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #1a5f3f;
    }

    /* Divisor */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1a5f3f, transparent);
    }

    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f8f9fa;
    }

    ::-webkit-scrollbar-thumb {
        background: #6b9b7f;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #1a5f3f;
    }

    /* Estilo para os checkboxes */
    [data-testid="stSidebar"] .stCheckbox {
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stSidebar"] .stCheckbox label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Função para adicionar marca d'água GIGANTE e estilizar gráficos
def add_watermark_and_style(fig, logo_base64=None):
    """
    Adiciona marca d'água MUITO GRANDE cobrindo todo o gráfico
    """
    if logo_base64:
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{logo_base64}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                sizex=1.75,  # 120% do tamanho do gráfico
                sizey=1.75,  # 120% do tamanho do gráfico
                xanchor="center",
                yanchor="middle",
                opacity=0.08,  # <<< AQUI VOCÊ ALTERA A OPACIDADE DA MARCA D'ÁGUA
                layer="below"
            )
        )

    # Estilização elegante
    fig.update_layout(
        plot_bgcolor='rgba(248, 246, 241, 0.5)',
        paper_bgcolor='white',
        font=dict(
            family="Inter, sans-serif",
            size=12,
            color="#2c2c2c"
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Inter, sans-serif",
            bordercolor="#6b9b7f"
        ),
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(color="#e0ddd5", width=2),
                fillcolor="rgba(0,0,0,0)"
            )
        ]
    )

    # Estilizar eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(224, 221, 213, 0.5)',
        showline=True,
        linewidth=2,
        linecolor='#e0ddd5',
        title_font=dict(size=13, color="#1a5f3f", family="Inter"),
        tickfont=dict(size=11, color="#6b9b7f")
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(224, 221, 213, 0.5)',
        showline=True,
        linewidth=2,
        linecolor='#e0ddd5',
        title_font=dict(size=13, color="#1a5f3f", family="Inter"),
        tickfont=dict(size=11, color="#6b9b7f")
    )

    return fig

# Função para limpar CNPJ
def limpar_cnpj(cnpj):
    if not cnpj:
        return ""
    return re.sub(r'\D', '', cnpj)

# Função para converter data brasileira para formato API
def formatar_data_api(data_str):
    if not data_str:
        return None
    data_limpa = re.sub(r'\D', '', data_str)
    if len(data_limpa) == 8:
        try:
            dia = data_limpa[:2]
            mes = data_limpa[2:4]
            ano = data_limpa[4:]
            datetime.strptime(f"{dia}/{mes}/{ano}", '%d/%m/%Y')
            return f"{ano}{mes}{dia}"
        except ValueError:
            return None
    return None

# Função para buscar data anterior disponível
def buscar_data_anterior(df, data_alvo):
    datas_disponiveis = df['DT_COMPTC']
    datas_anteriores = datas_disponiveis[datas_disponiveis <= data_alvo]
    if len(datas_anteriores) > 0:
        return datas_anteriores.idxmax()
    return None

# Função para ajustar período de análise (SEM MOSTRAR NOTIFICAÇÃO)
def ajustar_periodo_analise(df, data_inicial_str, data_final_str):
    data_inicial = datetime.strptime(data_inicial_str, '%Y%m%d')
    data_final = datetime.strptime(data_final_str, '%Y%m%d')
    idx_inicial = buscar_data_anterior(df, data_inicial)
    idx_final = buscar_data_anterior(df, data_final)

    ajustes = {
        'data_inicial_original': data_inicial,
        'data_final_original': data_final,
        'data_inicial_usada': None,
        'data_final_usada': None,
        'houve_ajuste_inicial': False,
        'houve_ajuste_final': False
    }

    if idx_inicial is not None:
        ajustes['data_inicial_usada'] = df.loc[idx_inicial, 'DT_COMPTC']
        ajustes['houve_ajuste_inicial'] = ajustes['data_inicial_usada'].date() != data_inicial.date()

    if idx_final is not None:
        ajustes['data_final_usada'] = df.loc[idx_final, 'DT_COMPTC']
        ajustes['houve_ajuste_final'] = ajustes['data_final_usada'].date() != data_final.date()

    if idx_inicial is not None and idx_final is not None:
        df_filtrado = df.loc[idx_inicial:idx_final].copy()
        return df_filtrado, ajustes

    return df, ajustes

# Função para obter dados do CDI
@st.cache_data
def obter_dados_cdi(data_ini, data_fim):
    """
    Obtém dados diários do CDI através da API do Banco Central

    Args:
        data_ini (str): Data inicial no formato 'YYYYMMDD'
        data_fim (str): Data final no formato 'YYYYMMDD'

    Returns:
        DataFrame: DataFrame com os dados do CDI
    """
    # Converter datas para o formato esperado pela API
    data_ini_dt = datetime.strptime(data_ini, '%Y%m%d')
    data_fim_dt = datetime.strptime(data_fim, '%Y%m%d')

    data_ini_api = data_ini_dt.strftime('%d/%m/%Y')
    data_fim_api = data_fim_dt.strftime('%d/%m/%Y')

    # URL da API do BCB para a série do CDI (código 12)
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={data_ini_api}&dataFinal={data_fim_api}"

    try:
        # Fazer requisição à API
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))

        # Criar DataFrame
        df_cdi = pd.DataFrame(data)

        # Converter tipos de dados
        df_cdi['data'] = pd.to_datetime(df_cdi['data'], format='%d/%m/%Y')
        df_cdi['valor'] = df_cdi['valor'].astype(float)

        # Renomear colunas
        df_cdi.rename(columns={'valor': 'CDI', 'data': 'DT_COMPTC'}, inplace=True)

        # Converter taxa diária para decimal
        df_cdi['CDI_decimal'] = df_cdi['CDI'] / 100

        # Calcular rentabilidade acumulada
        df_cdi['CDI_acum'] = (1 + df_cdi['CDI_decimal']).cumprod() - 1
        df_cdi['CDI_acum_pct'] = df_cdi['CDI_acum'] * 100

        return df_cdi

    except Exception as e:
        st.error(f"Erro ao obter dados do CDI: {str(e)}")
        return pd.DataFrame()

# Função para obter dados da Selic
@st.cache_data
def obter_dados_selic(data_ini, data_fim):
    """
    Obtém dados diários da Selic através da API do Banco Central

    Args:
        data_ini (str): Data inicial no formato 'YYYYMMDD'
        data_fim (str): Data final no formato 'YYYYMMDD'

    Returns:
        DataFrame: DataFrame com os dados da Selic
    """
    # Converter datas para o formato esperado pela API
    data_ini_dt = datetime.strptime(data_ini, '%Y%m%d')
    data_fim_dt = datetime.strptime(data_fim, '%Y%m%d')

    data_ini_api = data_ini_dt.strftime('%d/%m/%Y')
    data_fim_api = data_fim_dt.strftime('%d/%m/%Y')

    # URL da API do BCB para a série da Selic (código 11)
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={data_ini_api}&dataFinal={data_fim_api}"

    try:
        # Fazer requisição à API
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))

        # Criar DataFrame
        df_selic = pd.DataFrame(data)

        # Converter tipos de dados
        df_selic['data'] = pd.to_datetime(df_selic['data'], format='%d/%m/%Y')
        df_selic['valor'] = df_selic['valor'].astype(float)

        # Renomear colunas
        df_selic.rename(columns={'valor': 'SELIC', 'data': 'DT_COMPTC'}, inplace=True)

        # Converter taxa diária para decimal
        df_selic['SELIC_decimal'] = df_selic['SELIC'] / 100

        # Calcular rentabilidade acumulada
        df_selic['SELIC_acum'] = (1 + df_selic['SELIC_decimal']).cumprod() - 1
        df_selic['SELIC_acum_pct'] = df_selic['SELIC_acum'] * 100

        return df_selic

    except Exception as e:
        st.error(f"Erro ao obter dados da Selic: {str(e)}")
        return pd.DataFrame()

# Função para normalizar e alinhar séries temporais
def normalizar_e_alinhar_series(df_fundo, df_cdi, df_selic):
    """
    Normaliza e alinha as séries temporais do fundo, CDI e Selic

    Args:
        df_fundo (DataFrame): DataFrame com os dados do fundo
        df_cdi (DataFrame): DataFrame com os dados do CDI
        df_selic (DataFrame): DataFrame com os dados da Selic

    Returns:
        tuple: (df_fundo, df_cdi, df_selic) normalizados e alinhados
    """
    # Encontrar a data comum mais recente entre as três séries
    datas_fundo = set(df_fundo['DT_COMPTC'].dt.date)
    datas_cdi = set(df_cdi['DT_COMPTC'].dt.date) if not df_cdi.empty else set()
    datas_selic = set(df_selic['DT_COMPTC'].dt.date) if not df_selic.empty else set()

    # Se não temos dados de CDI ou Selic, retornar apenas o fundo
    if not datas_cdi and not datas_selic:
        return df_fundo, pd.DataFrame(), pd.DataFrame()

    # Encontrar datas comuns
    datas_comuns = datas_fundo
    if datas_cdi:
        datas_comuns = datas_comuns.intersection(datas_cdi)
    if datas_selic:
        datas_comuns = datas_comuns.intersection(datas_selic)

    if not datas_comuns:
        st.warning("Não há datas em comum entre o fundo e os indicadores. Usando a data inicial do fundo.")
        data_inicial = min(df_fundo['DT_COMPTC'].dt.date)
    else:
        data_inicial = min(datas_comuns)

    # Filtrar os DataFrames a partir da data comum
    df_fundo = df_fundo[df_fundo['DT_COMPTC'].dt.date >= data_inicial].copy()

    if not df_cdi.empty:
        df_cdi = df_cdi[df_cdi['DT_COMPTC'].dt.date >= data_inicial].copy()

    if not df_selic.empty:
        df_selic = df_selic[df_selic['DT_COMPTC'].dt.date >= data_inicial].copy()

    # Criar um índice de datas completo
    todas_datas = sorted(list(set(df_fundo['DT_COMPTC'].dt.date) | 
                              set(df_cdi['DT_COMPTC'].dt.date if not df_cdi.empty else []) | 
                              set(df_selic['DT_COMPTC'].dt.date if not df_selic.empty else [])))

    # Reindexar os DataFrames para incluir todas as datas
    df_fundo_completo = df_fundo.set_index('DT_COMPTC')
    df_cdi_completo = df_cdi.set_index('DT_COMPTC') if not df_cdi.empty else pd.DataFrame()
    df_selic_completo = df_selic.set_index('DT_COMPTC') if not df_selic.empty else pd.DataFrame()

    # Criar DataFrames com todas as datas
    idx = pd.DatetimeIndex(todas_datas)

    # Reindexar e preencher valores ausentes com o último valor disponível
    if not df_fundo_completo.empty:
        df_fundo_completo = df_fundo_completo.reindex(idx, method='ffill')
        df_fundo_completo.reset_index(inplace=True)
        df_fundo_completo.rename(columns={'index': 'DT_COMPTC'}, inplace=True)

    if not df_cdi.empty and not df_cdi_completo.empty:
        df_cdi_completo = df_cdi_completo.reindex(idx, method='ffill')
        df_cdi_completo.reset_index(inplace=True)
        df_cdi_completo.rename(columns={'index': 'DT_COMPTC'}, inplace=True)

    if not df_selic.empty and not df_selic_completo.empty:
        df_selic_completo = df_selic_completo.reindex(idx, method='ffill')
        df_selic_completo.reset_index(inplace=True)
        df_selic_completo.rename(columns={'index': 'DT_COMPTC'}, inplace=True)

    # Normalizar as séries (base 100)
    if not df_fundo_completo.empty:
        valor_inicial_fundo = df_fundo_completo['VL_QUOTA'].iloc[0]
        df_fundo_completo['VL_QUOTA_NORM'] = (df_fundo_completo['VL_QUOTA'] / valor_inicial_fundo - 1) * 100

    if not df_cdi.empty and not df_cdi_completo.empty:
        valor_inicial_cdi = df_cdi_completo['CDI_acum'].iloc[0]
        df_cdi_completo['CDI_NORM'] = ((df_cdi_completo['CDI_acum'] - valor_inicial_cdi) / (1 + valor_inicial_cdi)) * 100

    if not df_selic.empty and not df_selic_completo.empty:
        valor_inicial_selic = df_selic_completo['SELIC_acum'].iloc[0]
        df_selic_completo['SELIC_NORM'] = ((df_selic_completo['SELIC_acum'] - valor_inicial_selic) / (1 + valor_inicial_selic)) * 100

    return df_fundo_completo, df_cdi_completo, df_selic_completo

# Sidebar com logo (SEM título "Configurações")
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

# Input de CNPJ
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value="",
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação"
)

# Inputs de data
st.sidebar.markdown("#### 📅 Período de Análise")
col1_sidebar, col2_sidebar = st.sidebar.columns(2)

with col1_sidebar:
    data_inicial_input = st.text_input(
        "Data Inicial",
        value="",
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        key="data_inicial"
    )

with col2_sidebar:
    data_final_input = st.text_input(
        "Data Final",
        value="",
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        key="data_final"
    )

# Opções de indicadores (ADICIONADO AQUI!)
st.sidebar.markdown("#### 📈 Indicadores de Comparação")
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)
mostrar_selic = st.sidebar.checkbox("Comparar com Selic", value=False)

st.sidebar.markdown("---")

# Processar inputs
cnpj_limpo = limpar_cnpj(cnpj_input)
data_inicial_formatada = formatar_data_api(data_inicial_input)
data_final_formatada = formatar_data_api(data_final_input)

# Validação
cnpj_valido = False
datas_validas = False

if cnpj_input:
    if len(cnpj_limpo) != 14:
        st.sidebar.error("❌ CNPJ deve conter 14 dígitos")
    else:
        st.sidebar.success(f"✅ CNPJ: {cnpj_limpo}")
        cnpj_valido = True

if data_inicial_input and data_final_input:
    if not data_inicial_formatada or not data_final_formatada:
        st.sidebar.error("❌ Formato de data inválido. Use DD/MM/AAAA")
    else:
        try:
            dt_ini = datetime.strptime(data_inicial_formatada, '%Y%m%d')
            dt_fim = datetime.strptime(data_final_formatada, '%Y%m%d')
            if dt_ini > dt_fim:
                st.sidebar.error("❌ Data inicial deve ser anterior à data final")
            else:
                st.sidebar.success(f"✅ Período: {dt_ini.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}")
                datas_validas = True
        except:
            st.sidebar.error("❌ Erro ao processar datas")

# Botão para carregar dados
carregar_button = st.sidebar.button("🔄 Carregar Dados", type="primary", disabled=not (cnpj_valido and datas_validas))

# Título principal
st.markdown("<h1>📊 Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
st.markdown("---")

# Função para carregar dados
@st.cache_data
def carregar_dados_api(cnpj, data_ini, data_fim):
    dt_inicial = datetime.strptime(data_ini, '%Y%m%d')
    dt_ampliada = dt_inicial - timedelta(days=60)
    data_ini_ampliada = dt_ampliada.strftime('%Y%m%d')

    url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini_ampliada}/{data_fim}/"
    req = urllib.request.Request(url)
    req.add_header('Accept-Encoding', 'gzip')
    req.add_header('Authorization', 'Bearer caianfrancodecamargo@gmail.com')

    response = urllib.request.urlopen(req)

    if response.info().get('Content-Encoding') == 'gzip':
        buf = BytesIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        content_json = json.loads(f.read().decode("utf-8"))
    else:
        content = response.read().decode("utf-8")
        content_json = json.loads(content)

    df = pd.DataFrame(content_json)
    if 'DT_COMPTC' in df.columns:
        df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'])

    return df

# Funções de formatação
def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_pct_port(x):
    return f"{x*100:.2f}%".replace('.', ',')

# Verificar se deve carregar os dados
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False

if carregar_button and cnpj_valido and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpj = cnpj_limpo
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada
    st.session_state.mostrar_cdi = mostrar_cdi
    st.session_state.mostrar_selic = mostrar_selic

if not st.session_state.dados_carregados:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")

    st.markdown("""
    ### 📋 Como usar:

    1. **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar
    2. **Data Inicial**: Digite a data inicial no formato DD/MM/AAAA
    3. **Data Final**: Digite a data final no formato DD/MM/AAAA
    4. **Indicadores**: Selecione os indicadores para comparação (CDI/Selic)
    5. Clique em **Carregar Dados** para visualizar as análises

    ---

    ### 📊 Análises disponíveis:
    - Rentabilidade histórica e CAGR
    - Análise de risco (Drawdown, Volatilidade, VaR)
    - Evolução patrimonial e captação
    - Perfil de cotistas
    - Retornos em janelas móveis
    """)

    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
        # Carregar dados do fundo
        df_completo = carregar_dados_api(st.session_state.cnpj, st.session_state.data_ini, st.session_state.data_fim)
        df, ajustes = ajustar_periodo_analise(df_completo, st.session_state.data_ini, st.session_state.data_fim)

        # Carregar dados do CDI e Selic se necessário
        df_cdi = pd.DataFrame()
        df_selic = pd.DataFrame()

        if st.session_state.mostrar_cdi:
            df_cdi = obter_dados_cdi(st.session_state.data_ini, st.session_state.data_fim)

        if st.session_state.mostrar_selic:
            df_selic = obter_dados_selic(st.session_state.data_ini, st.session_state.data_fim)

        # Normalizar e alinhar as séries
        df, df_cdi, df_selic = normalizar_e_alinhar_series(df, df_cdi, df_selic)

    # Preparação dos dados
    df = df.sort_values('DT_COMPTC').reset_index(drop=True)
    primeira_cota = df['VL_QUOTA'].iloc[0]
    df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota) - 1) * 100

    # Calcular métricas
    df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
    df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
    df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
    df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

    vol_window = 21
    trading_days = 252
    df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()
    df['Volatilidade'] = df['VL_QUOTA'].pct_change().rolling(vol_window).std() * np.sqrt(trading_days) * 100
    vol_hist = round(df['Variacao_Perc'].std() * np.sqrt(trading_days) * 100, 2)

    # CAGR
    df_cagr = df.copy()
    end_value = df_cagr['VL_QUOTA'].iloc[-1]
    df_cagr['dias_uteis'] = df_cagr.index[-1] - df_cagr.index
    df_cagr = df_cagr[df_cagr['dias_uteis'] >= 252].copy()
    df_cagr['CAGR'] = ((end_value / df_cagr['VL_QUOTA']) ** (252 / df_cagr['dias_uteis'])) - 1
    df_cagr['CAGR'] = df_cagr['CAGR'] * 100
    mean_cagr = df_cagr['CAGR'].mean()

    # VaR
    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot = df.dropna(subset=['Retorno_21d']).copy()
    VaR_95 = np.percentile(df_plot['Retorno_21d'], 5)
    VaR_99 = np.percentile(df_plot['Retorno_21d'], 1)
    ES_95 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
    ES_99 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()

    # Cores
    color_primary = '#1a5f3f'
    color_secondary = '#6b9b7f'
    color_danger = '#dc3545'
    color_cdi = '#f0b429'
    color_selic = '#457b9d'

    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Patrimônio Líquido", format_brl(df['VL_PATRIM_LIQ'].iloc[-1]))

    with col2:
        st.metric("👥 Número de Cotistas", f"{int(df['NR_COTST'].iloc[-1]):,}".replace(',', '.'))

    with col3:
        st.metric("📈 CAGR Médio", f"{mean_cagr:.2f}%")

    with col4:
        st.metric("📊 Volatilidade Histórica", f"{vol_hist:.2f}%")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Rentabilidade",
        "📉 Risco",
        "💰 Patrimônio",
        "👥 Cotistas",
        "🎯 Janelas Móveis"
    ])

    with tab1:
        st.subheader("📈 Rentabilidade Histórica")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_QUOTA_NORM'],
            mode='lines',
            name='Fundo',
            line=dict(color=color_primary, width=2.5),
            fill='tozeroy',
            fillcolor=f'rgba(26, 95, 63, 0.1)',
            hovertemplate='<b>Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
        ))

        # Adicionar CDI se selecionado
        if st.session_state.mostrar_cdi and not df_cdi.empty:
            fig1.add_trace(go.Scatter(
                x=df_cdi['DT_COMPTC'],
                y=df_cdi['CDI_NORM'],
                mode='lines',
                name='CDI',
                line=dict(color=color_cdi, width=2, dash='dash'),
                hovertemplate='<b>CDI</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
            ))

        # Adicionar Selic se selecionado
        if st.session_state.mostrar_selic and not df_selic.empty:
            fig1.add_trace(go.Scatter(
                x=df_selic['DT_COMPTC'],
                y=df_selic['SELIC_NORM'],
                mode='lines',
                name='Selic',
                line=dict(color=color_selic, width=2, dash='dash'),
                hovertemplate='<b>Selic</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
            ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig1 = add_watermark_and_style(fig1, logo_base64)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 CAGR Anual por Dia de Aplicação")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_cagr['DT_COMPTC'],
            y=df_cagr['CAGR'],
            mode='lines',
            name='CAGR do Fundo',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='<b>CAGR do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
        ))
        fig2.add_trace(go.Scatter(
            x=df_cagr['DT_COMPTC'],
            y=[mean_cagr] * len(df_cagr),
            mode='lines',
            line=dict(dash='dash', color=color_secondary, width=2),
            name=f'CAGR Médio ({mean_cagr:.2f}%)'
        ))

        # Adicionar CDI anualizado se selecionado
        if st.session_state.mostrar_cdi and not df_cdi.empty:
            # Calcular CDI anualizado para cada data
            cdi_anual = []
            for i, row in df_cagr.iterrows():
                data_atual = row['DT_COMPTC']
                data_inicial = df_cagr['DT_COMPTC'].iloc[0]
                dias_passados = (data_atual - data_inicial).days

                if dias_passados > 0:
                    # Encontrar o valor do CDI acumulado para esta data
                    cdi_acum = df_cdi[df_cdi['DT_COMPTC'] <= data_atual]['CDI_acum'].iloc[-1]

                    # Anualizar o CDI (considerando dias úteis)
                    dias_uteis = row['dias_uteis']
                    if dias_uteis >= 252:
                        cdi_anual_valor = ((1 + cdi_acum) ** (252 / dias_uteis) - 1) * 100
                        cdi_anual.append(cdi_anual_valor)
                    else:
                        cdi_anual.append(None)
                else:
                    cdi_anual.append(None)

            # Adicionar ao gráfico apenas os valores válidos
            df_cdi_anual = pd.DataFrame({
                'DT_COMPTC': df_cagr['DT_COMPTC'],
                'CDI_anual': cdi_anual
            }).dropna()

            if not df_cdi_anual.empty:
                fig2.add_trace(go.Scatter(
                    x=df_cdi_anual['DT_COMPTC'],
                    y=df_cdi_anual['CDI_anual'],
                    mode='lines',
                    name='CDI Anualizado',
                    line=dict(color=color_cdi, width=2, dash='dash'),
                    hovertemplate='<b>CDI Anualizado</b><br>Data: %{x|%d/%m/%Y}<br>Taxa: %{y:.2f}%<extra></extra>'
                ))

        fig2.update_layout(
            xaxis_title="Data",
            yaxis_title="CAGR (% a.a)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig2 = add_watermark_and_style(fig2, logo_base64)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("📉 Drawdown Histórico")

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Drawdown'],
            mode='lines',
            name='Drawdown do Fundo',
            line=dict(color=color_danger, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(220, 53, 69, 0.1)',
            hovertemplate='<b>Drawdown do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
        ))

        # Adicionar Drawdown do CDI se selecionado
        if st.session_state.mostrar_cdi and not df_cdi.empty:
            # Calcular Drawdown do CDI
            df_cdi['CDI_Max'] = df_cdi['CDI_acum'].cummax()
            df_cdi['CDI_Drawdown'] = (df_cdi['CDI_acum'] / df_cdi['CDI_Max'] - 1) * 100

            fig3.add_trace(go.Scatter(
                x=df_cdi['DT_COMPTC'],
                y=df_cdi['CDI_Drawdown'],
                mode='lines',
                name='Drawdown do CDI',
                line=dict(color=color_cdi, width=2, dash='dash'),
                hovertemplate='<b>Drawdown do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))

        fig3.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

        fig3.update_layout(
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig3 = add_watermark_and_style(fig3, logo_base64)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"📊 Volatilidade Móvel ({vol_window} dias úteis)")

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Volatilidade'],
            mode='lines',
            name=f'Volatilidade do Fundo ({vol_window} dias)',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='<b>Volatilidade do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
        ))

        fig4.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=[vol_hist] * len(df),
            mode='lines',
            line=dict(dash='dash', color=color_secondary, width=2),
            name=f'Vol. Histórica ({vol_hist:.2f}%)'
        ))

        # Adicionar Volatilidade do CDI se selecionado
        if st.session_state.mostrar_cdi and not df_cdi.empty and len(df_cdi) > vol_window:
            # Calcular volatilidade do CDI
            df_cdi['CDI_var'] = df_cdi['CDI_decimal'].pct_change()
            df_cdi['CDI_vol'] = df_cdi['CDI_var'].rolling(vol_window).std() * np.sqrt(trading_days) * 100
            cdi_vol_hist = round(df_cdi['CDI_var'].std() * np.sqrt(trading_days) * 100, 2)

            fig4.add_trace(go.Scatter(
                x=df_cdi['DT_COMPTC'],
                y=df_cdi['CDI_vol'],
                mode='lines',
                name=f'Volatilidade do CDI ({vol_window} dias)',
                line=dict(color=color_cdi, width=2, dash='dash'),
                hovertemplate='<b>Volatilidade do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ))

            fig4.add_trace(go.Scatter(
                x=df_cdi['DT_COMPTC'],
                y=[cdi_vol_hist] * len(df_cdi),
                mode='lines',
                line=dict(dash='dot', color=color_cdi, width=1.5),
                name=f'CDI Vol. Histórica ({cdi_vol_hist:.2f}%)'
            ))

        fig4.update_layout(
            xaxis_title="Data",
            yaxis_title="Volatilidade (% a.a.)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig4 = add_watermark_and_style(fig4, logo_base64)
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("⚠️ Value at Risk (VaR) e Expected Shortfall (ES)")

        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=df_plot['DT_COMPTC'],
            y=df_plot['Retorno_21d'] * 100,
            mode='lines',
            name='Rentabilidade móvel do Fundo (1m)',
            line=dict(color=color_primary, width=2),
            hovertemplate='<b>Rentabilidade do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade 21d: %{y:.2f}%<extra></extra>'
        ))
        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[VaR_95 * 100, VaR_95 * 100],
            mode='lines',
            name='VaR 95%',
            line=dict(dash='dot', color='orange', width=2)
        ))
        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[VaR_99 * 100, VaR_99 * 100],
            mode='lines',
            name='VaR 99%',
            line=dict(dash='dot', color='red', width=2)
        ))
        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[ES_95 * 100, ES_95 * 100],
            mode='lines',
            name='ES 95%',
            line=dict(dash='dash', color='orange', width=2)
        ))
        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[ES_99 * 100, ES_99 * 100],
            mode='lines',
            name='ES 99%',
            line=dict(dash='dash', color='red', width=2)
        ))

        # Adicionar retorno móvel do CDI se selecionado
        if st.session_state.mostrar_cdi and not df_cdi.empty and len(df_cdi) > 21:
            # Calcular retorno móvel de 21 dias do CDI
            df_cdi['CDI_retorno_21d'] = df_cdi['CDI_acum'].pct_change(21)
            df_cdi_plot = df_cdi.dropna(subset=['CDI_retorno_21d']).copy()

            if not df_cdi_plot.empty:
                fig5.add_trace(go.Scatter(
                    x=df_cdi_plot['DT_COMPTC'],
                    y=df_cdi_plot['CDI_retorno_21d'] * 100,
                    mode='lines',
                    name='Rentabilidade móvel do CDI (1m)',
                    line=dict(color=color_cdi, width=2, dash='dash'),
                    hovertemplate='<b>Rentabilidade do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade 21d: %{y:.2f}%<extra></extra>'
                ))

        fig5.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
            template="plotly_white",
            hovermode="x unified",
            height=600,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig5 = add_watermark_and_style(fig5, logo_base64)
        st.plotly_chart(fig5, use_container_width=True)

        st.info(f"""
        **Este gráfico mostra que, em um período de 1 mês:**

        • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR)**,
        e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES)**.

        • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR)**,
        e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_95)} (ES)**.
        """)

    with tab3:
        st.subheader("💰 Patrimônio e Captação Líquida")

        fig6 = go.Figure([
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Soma_Acumulada'],
                mode='lines',
                name='Captação Líquida',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Captação Líquida Acumulada: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['Soma_Acumulada']]
            ),
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_PATRIM_LIQ'],
                mode='lines',
                name='Patrimônio Líquido',
                line=dict(color=color_secondary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Líquido: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['VL_PATRIM_LIQ']]
            )
        ])

        fig6.update_layout(
            xaxis_title="Data",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig6 = add_watermark_and_style(fig6, logo_base64)
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("📊 Captação Líquida Mensal")

        df_monthly = df.groupby(pd.Grouper(key='DT_COMPTC', freq='M'))[['CAPTC_DIA', 'RESG_DIA']].sum()
        df_monthly['Captacao_Liquida'] = df_monthly['CAPTC_DIA'] - df_monthly['RESG_DIA']

        colors = [color_primary if x >= 0 else color_danger for x in df_monthly['Captacao_Liquida']]

        fig7 = go.Figure([
            go.Bar(
                x=df_monthly.index,
                y=df_monthly['Captacao_Liquida'],
                name='Captação Líquida Mensal',
                marker_color=colors,
                hovertemplate='Mês: %{x|%b/%Y}<br>Captação Líquida: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df_monthly['Captacao_Liquida']]
            )
        ])

        fig7.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig7 = add_watermark_and_style(fig7, logo_base64)
        st.plotly_chart(fig7, use_container_width=True)

    with tab4:
        st.subheader("👥 Patrimônio Médio e Nº de Cotistas")

        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Patrimonio_Liq_Medio'],
            mode='lines',
            name='Patrimônio Médio por Cotista',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Médio: %{customdata}<extra></extra>',
            customdata=[format_brl(v) for v in df['Patrimonio_Liq_Medio']]
        ))
        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['NR_COTST'],
            mode='lines',
            name='Número de Cotistas',
            line=dict(color=color_secondary, width=2.5),
            yaxis='y2',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Nº de Cotistas: %{y}<extra></extra>'
        ))

        fig8.update_layout(
            xaxis_title="Data",
            yaxis=dict(title="Patrimônio Médio por Cotista (R$)"),
            yaxis2=dict(title="Número de Cotistas", overlaying="y", side="right"),
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig8 = add_watermark_and_style(fig8, logo_base64)
        st.plotly_chart(fig8, use_container_width=True)

    with tab5:
        st.subheader("🎯 Retornos em Janelas Móveis")

        janelas = {
            "12 meses (252 dias)": 252,
            "24 meses (504 dias)": 504,
            "36 meses (756 dias)": 756,
            "48 meses (1008 dias)": 1008,
            "60 meses (1260 dias)": 1260
        }

        df_returns = df.copy()
        for nome, dias in janelas.items():
            df_returns[nome] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1

        janela_selecionada = st.selectbox("Selecione o período:", list(janelas.keys()))

        if not df_returns[janela_selecionada].dropna().empty:
            fig9 = go.Figure()
            fig9.add_trace(go.Scatter(
                x=df_returns['DT_COMPTC'],
                y=df_returns[janela_selecionada],
                mode='lines',
                name=f"Retorno do Fundo — {janela_selecionada}",
                line=dict(width=2.5, color=color_primary),
                fill='tozeroy',
                fillcolor=f'rgba(26, 95, 63, 0.1)',
                hovertemplate="<b>Retorno do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
            ))

            # Adicionar retorno do CDI na janela selecionada
            if st.session_state.mostrar_cdi and not df_cdi.empty:
                dias_janela = janelas[janela_selecionada]
                if len(df_cdi) > dias_janela:
                    # Calcular retorno do CDI na janela selecionada
                    df_cdi_returns = df_cdi.copy()
                    df_cdi_returns[janela_selecionada] = df_cdi_returns['CDI_acum'] / df_cdi_returns['CDI_acum'].shift(dias_janela) - 1
                    df_cdi_returns = df_cdi_returns.dropna(subset=[janela_selecionada])

                    if not df_cdi_returns.empty:
                        fig9.add_trace(go.Scatter(
                            x=df_cdi_returns['DT_COMPTC'],
                            y=df_cdi_returns[janela_selecionada],
                            mode='lines',
                            name=f"Retorno do CDI — {janela_selecionada}",
                            line=dict(width=2, color=color_cdi, dash='dash'),
                            hovertemplate="<b>Retorno do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                        ))

            fig9.update_layout(
                xaxis_title="Data",
                yaxis_title=f"Retorno {janela_selecionada}",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                yaxis=dict(tickformat=".2%"),
                font=dict(family="Inter, sans-serif"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            fig9 = add_watermark_and_style(fig9, logo_base64)
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        <strong>Dashboard desenvolvido com Streamlit e Plotly</strong>
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
        Análise de Fundos de Investimentos • Copaíba Invest • 2025
    </p>
</div>
""", unsafe_allow_html=True)
