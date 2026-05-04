import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 0. CONFIGURAÇÃO DE NAVEGAÇÃO ESPACIAL
# ==========================================
st.set_page_config(page_title="ALPHA | NEURAL SCANNER", page_icon="📡", layout="wide")

# CSS DE OUTRO PLANETA
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    
    /* Fundo e Container */
    .main { background-color: #05070a; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #00f2ff; }
    
    /* Tipografia Estelar */
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; letter-spacing: 2px; }
    .stMarkdown, p, span { font-family: 'JetBrains Mono', monospace; }
    
    /* Efeito de Vidro nos Cards */
    .metric-card {
        background: rgba(10, 20, 30, 0.7);
        border: 1px solid #00f2ff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.15);
        text-align: center;
    }
    
    /* Glow de sinal ativo */
    .signal-active {
        border: 2px solid #00ff41;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }

    /* Botões Alpha */
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #00f2ff, #0066ff);
        color: white;
        border: none;
        font-family: 'Orbitron';
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00f2ff; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SEGURANÇA E CONEXÃO (INVISIBLE ENGINE)
# ==========================================
try:
    API_TOKEN = st.secrets["SPORTMONKS_TOKEN"]
except:
    API_TOKEN = st.sidebar.text_input("🔑 ACESSO AO NÚCLEO", type="password")

# ==========================================
# 2. SIDEBAR - COMANDO DE MISSÃO
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: #00f2ff; font-size: 20px;'>ALPHA ENGINE v.X</h1>", unsafe_allow_html=True)
    st.markdown("---")
    data_operacao = st.date_input("🛰️ CICLO TEMPORAL", datetime.today())
    gatilho_confianca = st.slider("🎯 PRECISÃO QUÂNTICA", 50, 95, 75, 5)
    st.markdown("---")
    st.write("🌌 **GALÁXIA:** Atacado/Finanças")
    st.write("🥋 **ESTADO:** Em Combate")
    if st.button("REINICIAR VARREDURA"):
        st.cache_data.clear()

# ==========================================
# 3. LÓGICA DE DADOS (O CÉREBRO)
# ==========================================
@st.cache_data(ttl=300)
def fetch_alpha_data(data_target):
    url = f"https://api.sportmonks.com/v3/football/fixtures/date/{data_target}"
    params = {"api_token": API_TOKEN, "include": "odds.market;participants", "filters": "markets:1;bookmakers:2"}
    try:
        r = requests.get(url, params=params)
        return r.json().get("data", [])
    except: return []

# ==========================================
# 4. INTERFACE DE OUTRO MUNDO
# ==========================================
if not API_TOKEN:
    st.warning("⚠️ SISTEMA BLOQUEADO. AGUARDANDO CHAVE DE CRIPTOGRAFIA.")
    st.stop()

jogos = fetch_alpha_data(data_operacao.strftime('%Y-%m-%d'))

# HEADER DE ALTO IMPACTO
c1, c2 = st.columns([3, 1])
with c1:
    st.title("📡 NEURAL MARKET SCANNER")
    st.markdown(f"<span style='color: #00f2ff;'>SISTEMA ATIVO // {data_operacao.strftime('%A, %d %b %Y')}</span>", unsafe_allow_html=True)

# KPIs ESTILIZADOS
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown(f"<div class='metric-card'><h3>ALVOS</h3><h1 style='color:#00f2ff;'>{len(jogos)}</h1></div>", unsafe_allow_html=True)

# Processamento de Sinais
sinais = []
for j in jogos:
    pc = pf = 0.0
    oc = of = 0.0
    for o in j.get("odds", []):
        if str(o.get("label")) in ["Home", "1"]:
            oc = float(o.get("value", 0))
            pc = float(str(o.get("probability", "0")).replace("%",""))
        if str(o.get("label")) in ["Away", "2"]:
            of = float(o.get("value", 0))
            pf = float(str(o.get("probability", "0")).replace("%",""))
    
    if pc >= gatilho_confianca: sinais.append({"nome": j['name'], "direcao": "CASA", "odd": oc, "prob": pc})
    if pf >= gatilho_confianca: sinais.append({"nome": j['name'], "direcao": "FORA", "odd": of, "prob": pf})

with kpi2:
    st.markdown(f"<div class='metric-card'><h3>SINAIS</h3><h1 style='color:#00ff41;'>{len(sinais)}</h1></div>", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"<div class='metric-card'><h3>RISCO</h3><h1 style='color:#ff004c;'>{100-gatilho_confianca}%</h1></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ÁREA DE SINAIS (GRID DINÂMICO)
aba_sinais, aba_radar = st.tabs(["⚡ GATILHOS ALPHA", "🌐 RADAR COMPLETO"])

with aba_sinais:
    if not sinais:
        st.markdown("<div style='text-align:center; padding: 50px;'><h4>AGUARDANDO ONDAS DE ASSIMETRIA...</h4></div>", unsafe_allow_html=True)
    else:
        for s in sinais:
            # Gráfico de Gauge para cada sinal
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = s['prob'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"CONFIANÇA: {s['prob']}%", 'font': {'size': 14, 'color': '#00f2ff'}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#00f2ff"},
                    'bar': {'color': "#00ff41"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "#00f2ff",
                    'steps': [{'range': [0, 100], 'color': 'rgba(0, 242, 255, 0.1)'}]
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=40, b=20))

            with st.container():
                col_info, col_chart = st.columns([2, 1])
                with col_info:
                    st.markdown(f"""
                        <div class='metric-card signal-active' style='text-align: left;'>
                            <h2 style='margin:0; font-size: 22px;'>🎯 ALVO IDENTIFICADO: {s['nome']}</h2>
                            <h3 style='color: #00ff41;'>DIREÇÃO: VITÓRIA {s['direcao']}</h3>
                            <h4 style='margin:0;'>ODD ATUAL: {s['odd']}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                with col_chart:
                    st.plotly_chart(fig, use_container_width=True)

with aba_radar:
    # Tabela com visual Matrix
    if jogos:
        radar_data = []
        for j in jogos:
            # Simples processamento para a tabela
            radar_data.append({"ALVO": j['name'], "START": j.get('starting_at')})
        st.dataframe(pd.DataFrame(radar_data), use_container_width=True)
