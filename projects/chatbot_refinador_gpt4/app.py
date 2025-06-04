from graph_builder import build_graph

# Dicionário de grafos por tema
graphs = {
    "IA & Orquestração Inteligente": build_graph("rag_conhecimento"),
    "Cybersegurança": build_graph("base_cyberseguranca"),
    "Ranking Abras 2024": build_graph("rag_abras")  # 👈 novo tema incluído
}

# Pipeline de execução com tema
def run_pipeline(pergunta: str, tema: str) -> str:
    graph = graphs[tema]  # Seleciona o grafo correto com base no tema escolhido
    state = {"pergunta": pergunta}
    final_state = graph.invoke(state)
    return final_state["resposta"]
