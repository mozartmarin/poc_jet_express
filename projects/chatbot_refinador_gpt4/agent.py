from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-4")

def is_response_good(resposta):
    critico = llm.predict(f"A seguinte resposta é clara e útil? Responda apenas SIM ou NÃO:\n\n{resposta}")
    return "SIM" in critico.upper()
