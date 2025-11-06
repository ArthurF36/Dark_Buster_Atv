import os
import json
import requests
from openai import OpenAI

# ==============================
# CONFIGURAÇÕES
# ==============================

# Carrega a chave da API do ambiente (Codespaces Secret)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERRO: OPENAI_API_KEY não foi encontrada. Configure o secret corretamente.")
    exit(1)

# Inicializa o cliente OpenAI
client = OpenAI(api_key=api_key)

# Prompt interno para análise de padrões manipulativos
ANALYSIS_PROMPT = """
Você é um sistema de verificação automática de padrões de design manipulativo em websites (dark patterns).
Sua tarefa é analisar o conteúdo de um site (HTML, textos, scripts e layout descrito) e identificar se ele contém padrões manipulativos.
Responda sempre em JSON estruturado no seguinte formato:

{
  "manipulative_design": true/false,
  "patterns_detected": [
    {
      "name": "Nome do padrão",
      "description": "Breve descrição do padrão encontrado"
    }
  ],
  "confidence_level": "alta/média/baixa"
}

Regras de análise:
1. Identifique se o site contém ou não padrões manipulativos.
2. Se encontrar, descreva cada padrão de forma clara e breve. Exemplos comuns:
   - 'Confirmshaming'
   - 'Roach Motel'
   - 'Scarcity'
   - 'Obstruction'
   - 'Sneaking'
3. Sempre inclua um nível de confiança: alta, média ou baixa.
4. Se não houver manipulação clara, retorne "manipulative_design": false.
Sua saída deve ser sempre somente o JSON, sem explicações adicionais.
"""

# ==============================
# FUNÇÕES PRINCIPAIS
# ==============================

def fetch_html(url: str) -> str:
    """Baixa o HTML de uma URL simulando um navegador real."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"✅ HTML obtido com sucesso ({len(response.text)} caracteres).")
        return response.text

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar o site ({url}): {e}")
        return ""

def analyze_site_with_ai(url: str):
    """Envia o HTML e o prompt para a IA generativa e retorna a análise."""
    html_content = fetch_html(url)
    if not html_content:
        return None

    # Combina o prompt com o conteúdo do site
    user_input = f"{ANALYSIS_PROMPT}\n\nAqui está o conteúdo do site:\n{html_content}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # pode alterar para "gpt-4.1" se disponível
            messages=[
                {"role": "system", "content": "Você é um assistente que analisa padrões manipulativos em websites."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=700
        )

        ai_response = response.choices[0].message.content.strip()

        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            print("⚠️ A resposta da IA não veio como JSON válido:")
            print(ai_response)
            return None

    except Exception as e:
        print(f"❌ Erro na chamada à API: {e}")
        return None


# ==============================
# EXECUÇÃO PRINCIPAL
# ==============================

if __name__ == "__main__":
    url = input("Digite a URL do site a ser analisado: ").strip()
    result = analyze_site_with_ai(url)

    if result:
        print("\n🧠 Resultado da análise:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Não foi possível obter a análise.")
