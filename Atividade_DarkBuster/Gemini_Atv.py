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
# FUNÇÃO PARA ANÁLISE COM JSON PADRÃO
# ============================================
def analisar_site(url):
    html = obter_html(url)

    # Se o HTML falhar, retornar JSON formal exigido pela atividade
    if not html:
        fallback = {
            "manipulative_design": False,
            "patterns_detected": [],
            "security_risks": [
                "Não foi possível acessar o site ou o acesso foi bloqueado."
            ],
            "confidence_level": "baixa"
        }
        print(json.dumps(fallback, indent=2, ensure_ascii=False))
        return

    print(f"✅ HTML obtido com sucesso ({len(html)} caracteres).")

    # Prompt no padrão exigido
    prompt = f"""
Você deve analisar o HTML abaixo e responder SOMENTE com um JSON válido.

Formato obrigatório:
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

REGRAS:
- A resposta deve ser APENAS JSON.
- Não use markdown.
- Não coloque nada antes ou depois do JSON.
- Não explique o resultado.

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
        print("\nResposta bruta:\n", data)

        # ===============================
        # TRATAMENTO DE RATE LIMIT (429)
        # ===============================
        if response.status_code == 429:
            erro_msg = data.get("error", {}).get("message", "").lower() if "error" in data else ""

            if "tokens per min" in erro_msg or "tpm" in erro_msg:
                fallback = {
                    "manipulative_design": False,
                    "patterns_detected": [],
                    "security_risks": [
                        "A análise não pôde ser realizada porque o limite de tokens por minuto (TPM) da API Gemini foi atingido."
                    ],
                    "confidence_level": "baixa"
                }
            else:
                fallback = {
                    "manipulative_design": False,
                    "patterns_detected": [],
                    "security_risks": [
                        "A análise não pôde ser realizada devido ao limite de requisições da API (rate limit)."
                    ],
                    "confidence_level": "baixa"
                }

            print(json.dumps(fallback, indent=2, ensure_ascii=False))
            return

        # ===============================
        # TRATAMENTO DE RESPOSTAS VÁLIDAS
        # ===============================
        if "candidates" in data:
            texto = data["candidates"][0]["content"]["parts"][0]["text"]

            print("\n🧠 JSON final:\n")
            print(texto)

            # Verifica se o JSON é válido
            try:
                json.loads(texto)
                print("\n✔ JSON válido!")
            except:
                print("\n⚠ JSON inválido (IA pode ter quebrado o formato).")

        else:
            print("⚠ Resposta fora do padrão.")
            fallback = {
                "manipulative_design": False,
                "patterns_detected": [],
                "security_risks": [
                    "A análise não pôde ser realizada; resposta fora do padrão da API Gemini."
                ],
                "confidence_level": "baixa"
            }
            print(json.dumps(fallback, indent=2, ensure_ascii=False))

    except Exception as e:
        print("❌ ERRO ao enviar para Gemini:", e)
        fallback = {
            "manipulative_design": False,
            "patterns_detected": [],
            "security_risks": [
                "Erro inesperado ao chamar a API Gemini."
            ],
            "confidence_level": "baixa"
        }
        print(json.dumps(fallback, indent=2, ensure_ascii=False))

# ============================================
# EXECUÇÃO
# ============================================
if __name__ == "__main__":
    url = input("Digite a URL do site a ser analisado: ").strip()
    analisar_site(url)
