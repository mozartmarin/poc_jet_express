from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from pathlib import Path

def get_retriever(pasta_nome: str):
    # Caminho dinâmico da base de conhecimento
    base_path = Path(f"data/{pasta_nome}")
    all_docs = []

    # Carrega arquivos .txt
    for file_path in base_path.glob("*.txt"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        all_docs.extend(loader.load())

    # Carrega arquivos .pdf
    for file_path in base_path.glob("*.pdf"):
        loader = PyPDFLoader(str(file_path))
        all_docs.extend(loader.load())

    # Divide em chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(all_docs)

    # Gera embeddings e armazena no FAISS
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    return vectorstore.as_retriever()
