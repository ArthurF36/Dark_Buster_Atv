import os
import requests
import json

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY não encontrada.")
    exit()

print("✅ GOOGLE_API_KEY foi detectada no ambiente!")
print(f"Tamanho da chave: {len(api_key)} caracteres")
print(f"Prefixo (seguro): {api_key[:5]}************ \n")

model = "gemini-2.5-flash"
url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Teste: diga 'Model OK!'"}
            ]
        }
    ]
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, json=payload)

print("Status:", response.status_code)
print("Resposta JSON:")
try:
    print(response.json())
except:
    print(response.text)
