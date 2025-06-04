import os
import time
import base64
from mistralai import Mistral
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Verificar se a chave da API foi carregada corretamente
if not api_key:
    raise ValueError("Erro: A chave da API MISTRAL_API_KEY não foi encontrada. Verifique seu arquivo .env.")

# Criar o cliente da Mistral
client = Mistral(api_key=api_key)

# Caminho do arquivo PDF a ser enviado
pdf_path = "data/nota-fiscal-notebook-dell.pdf"

# Verificar se o arquivo existe antes de tentar abrir
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"Erro: O arquivo '{pdf_path}' não foi encontrado. Verifique o caminho e tente novamente.")

# 1️⃣ Fazer upload do arquivo PDF para OCR
with open(pdf_path, "rb") as file:
    uploaded_pdf = client.files.upload(
        file={
            "file_name": "nota-fiscal-notebook-dell.pdf",
            "content": file
        },
        purpose="ocr"
    )

# Obter o ID do arquivo enviado
file_id = uploaded_pdf.id
print(f"✅ Arquivo enviado com sucesso! ID do arquivo: {file_id}")

# 2️⃣ Obter a URL assinada para o arquivo
signed_url = client.files.get_signed_url(file_id=file_id)
print(f"🔗 URL assinada gerada com sucesso: {signed_url.url}")

# 3️⃣ Enviar a URL assinada para a API de OCR e incluir imagens Base64
print("⏳ Enviando documento para OCR...")
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": signed_url.url
    },
    include_image_base64=True  # Ativar extração de imagens em Base64
)

# 4️⃣ Exibir o texto extraído pelo OCR
if ocr_response and hasattr(ocr_response, "pages"):
    for page in ocr_response.pages:
        print(f"\n📄 Página {page.index + 1}:")
        print(page.markdown)  # Exibir o conteúdo extraído em formato Markdown
        
        # Se houver imagens na página, salvar localmente
        if page.images:
            for image in page.images:
                if image.image_base64:
                    image_data = base64.b64decode(image.image_base64)
                    image_filename = f"data/ocr_image_page{page.index + 1}.jpeg"
                    with open(image_filename, "wb") as img_file:
                        img_file.write(image_data)
                    print(f"🖼️ Imagem salva: {image_filename}")
else:
    print("\n⚠️ O OCR não retornou texto. O documento pode conter apenas imagens.")
