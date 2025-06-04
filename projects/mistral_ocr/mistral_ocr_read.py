import json
import os
import base64
import re
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from mistralai import Mistral
from mistralai.models import ImageURLChunk, DocumentURLChunk, TextChunk

# 🔹 Carregar variáveis de ambiente do .env
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# 🔹 Verificar se a chave da API foi carregada corretamente
if not api_key:
    raise ValueError("Erro: A chave da API MISTRAL_API_KEY não foi encontrada. Verifique seu arquivo .env.")

# 🔹 Criar cliente Mistral
client = Mistral(api_key=api_key)

# 🔹 Função para converter imagem em Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 🔹 Função para processar arquivos PDF e Imagem com OCR
def process_file_with_ocr(file_path: str):
    file = Path(file_path)

    if not file.is_file():
        raise FileNotFoundError(f"Erro: O arquivo '{file_path}' não foi encontrado.")

    print(f"📄 Processando: {file_path}")

    if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        # 🔹 Redimensionar a imagem para otimização do OCR (opcional)
        image = Image.open(file_path)
        image_resized = image.resize((image.width // 2, image.height // 2))
        resized_path = f"data/resized_{file.name}"
        image_resized.save(resized_path)

        # 🔹 Converter imagem para Base64
        base64_image = encode_image_to_base64(resized_path)
        base64_data_url = f"data:image/png;base64,{base64_image}"

        # 🔹 Enviar imagem para OCR
        ocr_response = client.ocr.process(
            document=ImageURLChunk(image_url=base64_data_url),
            model="mistral-ocr-latest"
        )

    elif file.suffix.lower() == ".pdf":
        # 🔹 Fazer upload do PDF para o OCR
        uploaded_file = client.files.upload(
            file={"file_name": file.stem, "content": file.read_bytes()},
            purpose="ocr"
        )

        # 🔹 Obter URL assinada do arquivo
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

        # 🔹 Enviar PDF para OCR
        ocr_response = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest"
        )

    else:
        raise ValueError("Formato de arquivo não suportado. Apenas imagens (.jpg, .jpeg, .png) e PDFs são aceitos.")

    # 🔹 Extrair o texto OCR processado
    extracted_text = ocr_response.pages[0].markdown

    print("\n✅ Texto Extraído do OCR:")
    print(extracted_text)

    return extracted_text

# 🔹 Função para estruturar os dados extraídos
def structure_ocr_output(extracted_text):
    """
    Transforma o texto extraído do OCR em um JSON estruturado.
    """
    structured_response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    TextChunk(text=(
                        f"Este é o texto OCR extraído:\n{extracted_text}\n.\n"
                        "Transforme este texto em um JSON estruturado contendo:\n"
                        "- file_name: nome do arquivo\n"
                        "- topics: lista de tópicos\n"
                        "- languages: idioma identificado\n"
                        "- ocr_contents: dicionário com detalhes do recibo\n"
                        "Certifique-se de incluir data, hora, valores, número do ticket, método de pagamento, etc."
                    ))
                ]
            }
        ],
        response_format="json",  # ✅ Correção: Usar "json" ao invés de ResponseFormat.JSON
        temperature=0
    )

    # 🔹 Garantir que a resposta esteja estruturada corretamente
    response_dict = json.loads(structured_response.choices[0].message.content)
    return response_dict

# 🔹 Executar OCR e estruturar os dados
file_path = "data/receipt.png"  # Altere para qualquer PDF ou imagem que deseja processar
extracted_text = process_file_with_ocr(file_path)
structured_data = structure_ocr_output(extracted_text)

# 🔹 Salvar e exibir JSON formatado
output_json_path = "data/structured_output.json"
with open(output_json_path, "w", encoding="utf-8") as json_file:
    json.dump(structured_data, json_file, indent=4, ensure_ascii=False)

print("\n✅ Dados Estruturados pelo OCR:")
print(json.dumps(structured_data, indent=4, ensure_ascii=False))
print(f"\n📂 JSON salvo em: {output_json_path}")
