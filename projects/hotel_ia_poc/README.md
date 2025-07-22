# 🤖 Agente de IA para Hotelaria — Skyone

Este projeto é um MVP de agente conversacional de inteligência artificial treinado para atuar no setor hoteleiro. Ele responde perguntas operacionais sobre reservas, ocupação, check-ins, check-outs e métricas da diária média, utilizando linguagem natural em português.

A aplicação é executada localmente, com modelo LLM hospedado via [Ollama](https://ollama.com/) e interface construída com Streamlit.

---

## 💡 Funcionalidades

- Consulta de taxa de ocupação atual
- Check-ins e check-outs previstos para uma data específica
- Diária média e permanência média em períodos personalizáveis
- Listagem de hóspedes por data ou período
- Interação em linguagem natural
- Layout profissional com identidade visual da Empresa

---

## 📸 Interface

![Preview da interface](static/preview.png) <!-- opcional, coloque a imagem desejada -->

---

## ⚙️ Requisitos

- Python 3.10+
- [Ollama](https://ollama.com/) instalado com modelo `mistral`
- PostgreSQL com tabela `reservas` configurada

---

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/hotel-ia-agent.git
cd hotel-ia-agent
```
