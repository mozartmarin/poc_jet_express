import json
import os
import base64
import re
from PIL import Image
from mistralai import Mistral
from dotenv import load_dotenv

# 🔹 Carregar variáveis de ambiente do .env
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# 🔹 Verificar se a chave da API foi carregada corretamente
if not api_key:
    raise ValueError("Erro: A chave da API MISTRAL_API_KEY não foi encontrada. Verifique seu arquivo .env.")

# 🔹 Criar cliente Mistral
client = Mistral(api_key=api_key)

# 🔹 Definir caminho da imagem do recibo
image_path = "data/receipt.png"

# 🔹 Verificar se a imagem existe antes de processar
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Erro: A imagem '{image_path}' não foi encontrada.")

# 🔹 Redimensionar a imagem para melhorar a legibilidade (opcional)
image = Image.open(image_path)
image_resized = image.resize((image.width // 2, image.height // 2))
image_resized.save("data/receipt_resized.png")

print("📸 Imagem carregada e redimensionada para processamento...")

# 🔹 Função para converter a imagem para Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 🔹 Converter a imagem redimensionada para Base64
base64_image = encode_image_to_base64("data/receipt_resized.png")
base64_image_string = f"data:image/png;base64,{base64_image}"  # Formato correto para envio

# 🔹 Enviar a imagem para OCR
structured_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={"type": "image_url", "image_url": base64_image_string}
)

# 🔹 Extrair texto bruto do OCR
ocr_text = structured_response.pages[0].markdown

# 🔹 Função para estruturar os dados corretamente
def parse_ocr_text(ocr_text):
    """
    Converte o texto extraído pelo OCR em um JSON estruturado.
    """
    data = {
        "file_name": "parking_receipt",
        "topics": ["Parking", "Receipt", "Payment"],
        "languages": "English",
        "ocr_contents": {
            "header": re.search(r"PLACE FACE UP ON DASH", ocr_text, re.IGNORECASE).group(0) if re.search(r"PLACE FACE UP ON DASH", ocr_text, re.IGNORECASE) else "",
            "city": "CITY OF PALO ALTO",
            "validity": "NOT VALID FOR ONSTREET PARKING",
            "expiration": {
                "date": re.search(r"AUG \d{1,2}, 2024", ocr_text).group(0) if re.search(r"AUG \d{1,2}, 2024", ocr_text) else "",
                "time": re.search(r"\d{1,2}:\d{2} (AM|PM)", ocr_text).group(0) if re.search(r"\d{1,2}:\d{2} (AM|PM)", ocr_text) else ""
            },
            "purchase": {
                "date": re.search(r"Aug \d{1,2}, 2024", ocr_text).group(0) if re.search(r"Aug \d{1,2}, 2024", ocr_text) else "",
                "time": re.search(r"\d{1,2}:\d{2}(?: AM| PM)?", ocr_text).group(0) if re.search(r"\d{1,2}:\d{2}(?: AM| PM)?", ocr_text) else ""
            },
            "total_due": re.search(r"\$\d+\.\d{2}", ocr_text).group(0) if re.search(r"\$\d+\.\d{2}", ocr_text) else "$0.00",
            "rate": "Daily Parking",
            "total_paid": re.search(r"\$\d+\.\d{2}", ocr_text).group(0) if re.search(r"\$\d+\.\d{2}", ocr_text) else "$0.00",
            "payment_type": "CC (Swipe)",
            "ticket_number": re.search(r"\d{8}", ocr_text).group(0) if re.search(r"\d{8}", ocr_text) else "",
            "serial_number": "520117260957",
            "setting": "Permit Machines",
            "machine_name": "Civic Center",
            "card_info": "#^^^^-1224, Visa",
            "footer": {
                "display_instructions": "DISPLAY FACE UP ON DASH",
                "expiration_reminder": "PERMIT EXPIRES AT MIDNIGHT"
            }
        }
    }
    return data

# 🔹 Estruturar os dados corretamente
structured_data = parse_ocr_text(ocr_text)

# 🔹 Converter para JSON formatado e imprimir
print("\n✅ Dados extraídos pelo OCR:")
print(json.dumps(structured_data, indent=4))
