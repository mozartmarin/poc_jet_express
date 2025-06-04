import streamlit as st
from app import run_pipeline
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Chatbot Refinador GPT-4")

st.title("🤖 Chatbot com RAG + Refinamento de Resposta")

# 🔽 Seletor de tema com nova opção
tema = st.selectbox(
    "Selecione a base de conhecimento:",
    (
        "IA & Orquestração Inteligente",
        "Cybersegurança",
        "Ranking Abras 2024"
    )
)

# Campo de pergunta
pergunta = st.text_input("Digite sua pergunta:", "")

# Botão para executar
if st.button("Perguntar") and pergunta:
    with st.spinner("Processando..."):
        resposta = run_pipeline(pergunta, tema)
        st.success(resposta)
