import os
import requests
import json

# ============================================
# CONFIGURAÇÃO DA API GEMINI (v1beta REST)
# ============================================

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERRO: GOOGLE_API_KEY não encontrada!")
    exit(1)

modelo = "gemini-2.5-flash"
endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"


# ============================================
# FUNÇÃO PARA BAIXAR HTML
# ============================================

def obter_html(url):
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.text
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return None


# ============================================
# FUNÇÃO PARA ANALISAR HTML COM JSON PADRÃO
# ============================================

def analisar_site(url):
    html = obter_html(url)
    if not html:
        print("❌ Não foi possível obter o HTML.")
        return

    print(f"✅ HTML obtido com sucesso ({len(html)} caracteres).")

    # 🔥 PROMPT JSON PURO — CORRIGIDO COM {html}
    prompt = f"""
Você é um sistema de análise especializado e deve responder SOMENTE com JSON PURO, sem markdown, sem explicações e sem texto fora do JSON.

REGRAS IMPORTANTES:
- NÃO use ```json
- NÃO use ```
- NÃO adicione texto antes ou depois do JSON
- NÃO adicione comentários
- NÃO adicione campos extras
- Responda APENAS com um JSON puro válido

Analise o HTML abaixo e produza exclusivamente o seguinte formato JSON:

{{
  "manipulative_design": true/false,
  "patterns_detected": [
    {{
      "name": "Nome do padrão",
      "description": "Descrição curta"
    }}
  ],
  "security_risks": [
    "risco1",
    "risco2"
  ],
  "confidence_level": "alta/média/baixa"
}}

HTML analisado:
{html}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        print("Status da Gemini:", response.status_code)

        data = response.json()
        print("\nResposta JSON bruta:\n", data)

        if "candidates" in data:
            texto = data["candidates"][0]["content"]["parts"][0]["text"]

            print("\n🧠 JSON final:\n")
            print(texto)

            # Validação do JSON
            try:
                json.loads(texto)
                print("\n✔ JSON válido!")
            except:
                print("\n⚠ JSON inválido (IA pode ter adicionado texto extra).")

        else:
            print("⚠️ Resposta fora do padrão.")

    except Exception as e:
        print("❌ ERRO ao enviar para Gemini:", e)


if __name__ == "__main__":
    url = input("Digite a URL do site a ser analisado: ").strip()
    analisar_site(url)
