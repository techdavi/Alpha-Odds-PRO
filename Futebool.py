import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 1. SETUP INSTITUCIONAL (Layout Wide)
# ==========================================
st.set_page_config(page_title="Alpha Odds PRO", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# Injetando um pouco de CSS para deixar os botões e painéis mais "Premium"
st.markdown("""
    <style>
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border-left: 4px solid #00FF00;}
    .css-1d391kg { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BARRA LATERAL (CENTRAL DE COMANDO)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422160.png", width=60) # Ícone de radar
    st.title("⚙️ Painel de Controle")
    st.markdown("---")
    
    # Campo de senha mascarado (mais seguro)
    API_TOKEN = st.text_input("🔑 Sportmonks Token", type="password", help="Cole sua chave da API aqui")
    
    # Máquina do tempo: escolhe o dia da varredura
    data_alvo = st.date_input("📅 Data da Varredura", datetime.today())
    
    # Sensibilidade do Sniper
    gatilho_sniper = st.slider("🎯 Confiança Mínima (%)", min_value=50, max_value=95, value=70, step=5)
    
    st.markdown("---")
    st.caption("Alpha Odds Analytics © 2026")

# ==========================================
# 3. CABEÇALHO PRINCIPAL
# ==========================================
st.title("🎯 Alpha Odds | Institutional Scanner")
st.markdown("*Monitoramento algorítmico de assimetrias. Buscando o Edge em tempo real.*")

# ==========================================
# 4. MOTOR DE BUSCA
# ==========================================
@st.cache_data(ttl=300)
def buscar_jogos(data_formatada, token):
    if not token:
        return []
    
    url = f"https://api.sportmonks.com/v3/football/fixtures/date/{data_formatada}"
    parametros = {
        "api_token": token,
        "include": "odds.market;participants",
        "filters": "markets:1;bookmakers:2"
    }
    
    try:
        response = requests.get(url, params=parametros)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            st.sidebar.error(f"Erro API: {response.status_code}")
            return []
    except Exception as e:
        st.sidebar.error("Falha de conexão.")
        return []

# Executa a busca se tiver o Token
jogos = []
if API_TOKEN:
    jogos = buscar_jogos(data_alvo.strftime('%Y-%m-%d'), API_TOKEN)
else:
    st.info("👈 Insira sua chave (Token) no menu lateral para iniciar o sistema.")
    st.stop() # Trava o painel até a chave ser colocada

# ==========================================
# 5. PROCESSAMENTO DE DADOS E TABELA
# ==========================================
lista_sinais = []
tabela_geral = []

for jogo in jogos:
    nome = jogo.get("name", "Desconhecido")
    
    odd_casa = odd_fora = odd_empate = 0.0
    prob_casa = prob_fora = 0.0
    
    for odd in jogo.get("odds", []):
        label = str(odd.get("label", ""))
        if label in ["Home", "1"]:
            odd_casa = float(odd.get("value", 0))
            prob_str = str(odd.get("probability", "0%")).replace('%', '')
            prob_casa = float(prob_str) if prob_str else 0.0
        elif label in ["Away", "2"]:
            odd_fora = float(odd.get("value", 0))
            prob_str = str(odd.get("probability", "0%")).replace('%', '')
            prob_fora = float(prob_str) if prob_str else 0.0
        elif label in ["Draw", "X"]:
            odd_empate = float(odd.get("value", 0))
            
    # Guarda tudo para a tabela geral
    tabela_geral.append({
        "Jogo": nome,
        "Odd Casa": odd_casa,
        "Odd Empate": odd_empate,
        "Odd Fora": odd_fora,
        "Chance Casa": f"{prob_casa}%",
        "Chance Fora": f"{prob_fora}%"
    })

    # Filtra os sinais de acordo com o slider do usuário
    if prob_casa >= gatilho_sniper:
        lista_sinais.append({"jogo": nome, "lado": "CASA", "odd": odd_casa, "prob": prob_casa})
    elif prob_fora >= gatilho_sniper:
        lista_sinais.append({"jogo": nome, "lado": "FORA", "odd": odd_fora, "prob": prob_fora})

# ==========================================
# 6. DASHBOARD (MÉTRICAS NO TOPO)
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Radar Ativo", f"{len(jogos)} Jogos", "Hoje")
col2.metric("Oportunidades Alpha", len(lista_sinais), f"Acima de {gatilho_sniper}%")

maior_odd_alpha = max([s['odd'] for s in lista_sinais]) if lista_sinais else 0
col3.metric("Maior Odd Detectada", maior_odd_alpha, "Valor Alpha")

st.markdown("---")

# ==========================================
# 7. ABAS DO SISTEMA
# ==========================================
aba1, aba2 = st.tabs(["🟢 Sinais Sniper", "📋 Mercado Completo"])

with aba1:
    st.subheader(f"Gatilhos de Entrada (> {gatilho_sniper}%)")
    if not lista_sinais:
        st.warning("Mercado lateralizado/Sem assimetrias claras hoje. Preserve o capital.")
    else:
        for sinal in lista_sinais:
            with st.container():
                c1, c2 = st.columns([3, 1])
                c1.success(f"**Alvo:** {sinal['jogo']} | **Entrada:** Vitória {sinal['lado']}")
                c2.info(f"**Odd:** {sinal['odd']} (Confiança: {sinal['prob']}%)")

with aba2:
    st.subheader("Livro de Ofertas (Todos os Jogos)")
    if tabela_geral:
        df = pd.DataFrame(tabela_geral)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("Nenhum dado disponível para compilar a tabela.")