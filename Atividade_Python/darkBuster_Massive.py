import os
import requests
from bs4 import BeautifulSoup

# ==============================
# CONFIGURAÇÕES
# ==============================
API_URL = "https://api.massive.ai/v1/chat/completions"
API_KEY = os.getenv("MASSIVE_API_KEY")

if not API_KEY:
    raise EnvironmentError("❌ MASSIVE_API_KEY não encontrada. Defina-a antes de rodar o script.")

# ==============================
# FUNÇÕES
# ==============================
def obter_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"✅ HTML obtido com sucesso ({len(response.text)} caracteres).")
        return response.text
    except requests.RequestException as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return None


def analisar_html_com_massive(html):
    try:
        print("🤖 Enviando conteúdo para análise via Massive API...")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "meta-llama/Llama-3.1-70B-Instruct",
            "messages": [
                {"role": "system", "content": "Você é um analista de segurança web."},
                {"role": "user", "content": f"Analise o seguinte código HTML e descreva possíveis vulnerabilidades ou práticas inseguras:\n\n{html}"}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "⚠️ Nenhuma resposta válida recebida."
    except Exception as e:
        print(f"❌ Erro na chamada à Massive API: {e}")
        return None


# ==============================
# EXECUÇÃO PRINCIPAL
# ==============================
if __name__ == "__main__":
    url = input("Digite a URL do site a ser analisado: ").strip()
    html = obter_html(url)
    if html:
        resultado = analisar_html_com_massive(html)
        if resultado:
            print("\n🧩 Resultado da Análise:\n")
            print(resultado)
        else:
            print("❌ Não foi possível obter a análise.")
    else:
        print("❌ Não foi possível obter o HTML.")
