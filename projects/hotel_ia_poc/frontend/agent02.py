import sys
import os

import streamlit as st
st.set_page_config(page_title="Agente IA Hoteleiro", layout="wide")  # <-- AGORA é a 1ª chamada do Streamlit

from langchain_ollama import ChatOllama
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
import pandas as pd

# Caminho raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools import perguntas02 as perguntas
from db.connection import get_reservas

# ========= Cache de Dados =========

@st.cache_data(show_spinner="Carregando dados de reservas...")
def carregar_dados():
    df = get_reservas()
    df["data_checkin"] = pd.to_datetime(df["data_checkin"])
    df["data_checkout"] = pd.to_datetime(df["data_checkout"])
    return df

df_reservas = carregar_dados()

# ========= Prompt Base =========

with open("rag/prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# ========= LLM e Ferramentas =========

llm = ChatOllama(
    model="mistral",
    temperature=0,
    system_message=system_prompt
)

tools = [
    Tool(name="Taxa de Ocupação Hoje", func=lambda x: perguntas.get_taxa_ocupacao_hoje(df_reservas), description="Retorna a taxa de ocupação atual", return_direct=True),
    Tool(name="Check-ins de Hoje", func=lambda x: perguntas.get_checkins_hoje(df_reservas), description="Retorna número de check-ins previstos para hoje", return_direct=True),
    Tool(name="Check-outs de Hoje", func=lambda x: perguntas.get_checkouts_hoje(df_reservas), description="Retorna número de check-outs previstos para hoje", return_direct=True),
    Tool(name="Diária Média por Período", func=lambda x: perguntas.get_diaria_media(df_reservas), description="Retorna a diária média no período: semana, mês ou outro", return_direct=True),
    Tool(name="Permanência Média por Período", func=lambda x: perguntas.get_permanencia_media(df_reservas), description="Retorna a permanência média dos hóspedes no período", return_direct=True),
    Tool(name="Check-ins por Data", func=lambda x: perguntas.listar_checkins_por_data(df_reservas, x), description="Lista hóspedes com check-in em uma data específica", return_direct=True),
    Tool(name="Check-outs por Data", func=lambda x: perguntas.listar_checkouts_por_data(df_reservas, x), description="Lista hóspedes com check-out em uma data específica", return_direct=True),
    Tool(name="Hóspedes por Período", func=lambda x: perguntas.listar_hospedes_por_periodo(df_reservas, x), description="Lista hóspedes hospedados entre duas datas", return_direct=True),
    Tool(name="Consulta Genérica de Reservas", func=lambda x: perguntas.consultar_reservas(df_reservas, x), description="Consulta livre com expressões pandas, status, datas ou filtros", return_direct=True),
]

agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    max_iterations=10,
    handle_parsing_errors="Ignorar erro. Responda direto com o que você tiver em português."
)

# ========= Layout HTML =========

st.markdown("""
    <style>
    body { background-color: #0f1117; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
    .main-header {
        background: linear-gradient(90deg, #4f00ff 0%, #1e1b4b 100%);
        border-radius: 12px; padding: 2rem; margin-bottom: 1rem; text-align: center;
    }
    .main-header h1 { font-size: 2.2rem; color: white; margin-bottom: 0.4rem; }
    .main-header p { font-size: 1rem; color: #ddddff; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("static/logo_skyone.png", use_container_width=False, width=100)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<h1>Agente de Inteligência Artificial para Hotelaria</h1>", unsafe_allow_html=True)
st.markdown("<p>Converse em linguagem natural e obtenha insights com base em suas reservas.</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ========= Histórico =========

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).markdown(msg["content"])

# ========= Input =========

prompt = st.chat_input("Digite sua pergunta...")

if prompt and (len(st.session_state.chat_history) == 0 or prompt != st.session_state.chat_history[-1]["content"]):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            resposta = agent_executor.invoke({"input": prompt})
            st.markdown(resposta["output"])
            st.session_state.chat_history.append({"role": "assistant", "content": resposta["output"]})
        except Exception as e:
            erro = f"Erro ao processar a resposta: {e}"
            st.markdown(erro)
            st.session_state.chat_history.append({"role": "assistant", "content": erro})
