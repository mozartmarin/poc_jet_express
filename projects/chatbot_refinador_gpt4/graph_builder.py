from typing import TypedDict
from langgraph.graph import StateGraph
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

from retriever import get_retriever
from agent import is_response_good

load_dotenv()

# 🔁 Estado compartilhado entre nós
class ChatState(TypedDict):
    pergunta: str
    resposta: str

# 🔧 Construção do grafo para cada pasta temática
def build_graph(pasta: str):
    retriever = get_retriever(pasta)
    llm = ChatOpenAI(model_name="gpt-4")
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    # 🧠 Nó 1: Responde com base na pergunta
    def responder(state: ChatState) -> ChatState:
        resposta = qa_chain.run(state["pergunta"])
        return {"pergunta": state["pergunta"], "resposta": resposta}

    # ✅ Nó 2: Avalia se a resposta é boa
    def avaliar(state: ChatState) -> dict:
        return {"next": "finalizar"} if is_response_good(state["resposta"]) else {"next": "refinar"}

    # 🔁 Nó 3: Refina a pergunta para nova tentativa
    def refinar(state: ChatState) -> ChatState:
        nova_pergunta = llm.predict(f"Melhore a pergunta: {state['pergunta']}")
        return {"pergunta": nova_pergunta}

    # 🏁 Nó 4: Finaliza o fluxo e retorna o estado
    def finalizar(state: ChatState) -> ChatState:
        return state

    # 🔀 Criação do grafo
    workflow = StateGraph(state_schema=ChatState)
    workflow.add_node("responder", responder)
    workflow.add_node("avaliar", avaliar)
    workflow.add_node("refinar", refinar)
    workflow.add_node("finalizar", finalizar)

    workflow.set_entry_point("responder")
    workflow.set_finish_point("finalizar")

    workflow.add_edge("responder", "avaliar")
    workflow.add_conditional_edges(
        "avaliar",
        lambda s: s["next"],
        {
            "refinar": "refinar",
            "finalizar": "finalizar"
        }
    )
    workflow.add_edge("refinar", "responder")

    return workflow.compile()
