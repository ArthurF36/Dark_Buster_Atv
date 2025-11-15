import os
import requests
import json

# Pega a chave da OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY não encontrada.")
    exit()

print("✅ OPENAI_API_KEY foi detectada no ambiente!")
print(f"Tamanho da chave: {len(api_key)} caracteres")
print(f"Prefixo (seguro): {api_key[:5]}************ \n")

# Endpoint da OpenAI para GPT-4.1-mini
url = "https://api.openai.com/v1/responses"

# Payload no formato da API de Responses
payload = {
    "model": "gpt-4.1-mini",
    "input": "Teste: diga 'Model OK!'"
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

response = requests.post(url, headers=headers, json=payload)

print("Status:", response.status_code)
print("Resposta JSON:")
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)
