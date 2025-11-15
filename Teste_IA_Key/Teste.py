import os
import requests

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY não foi encontrada!")
    exit()

print("🔑 API_KEY detectada!")
print(f"Tamanho: {len(api_key)} caracteres")
print(f"Prefixo: {api_key[:5]}********")

print("\n⏳ Testando a API KEY...")

url = "https://generativelanguage.googleapis.com/v1/models?key=" + api_key

try:
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        print("✅ API KEY está funcionando!")
        print("Modelos encontrados:")
        data = response.json()
        for model in data.get("models", []):
            print(" -", model["name"])

    elif response.status_code == 401:
        print("❌ API KEY inválida ou sem permissão (401 Unauthorized).")
        print("Detalhes:", response.text)

    else:
        print("⚠️ API respondeu com erro.")
        print("Status:", response.status_code)
        print("Resposta:", response.text)

except requests.exceptions.RequestException as e:
    print("❌ Erro de conexão ao acessar a API do Gemini.")
    print("Detalhes:", e)
