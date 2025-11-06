import requests
import google.generativeai as genai
import os

# ============================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================

# Lê a chave da variável de ambiente
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERRO: GEMINI_API_KEY não encontrada no ambiente!")
    exit(1)

# Configura a API
genai.configure(api_key=api_key)

# Escolhe o modelo — será ajustado automaticamente se o flash não existir
modelo_escolhido = "gemini-1.5-flash"
modelos_disponiveis = [m.name for m in genai.list_models()]

if f"models/{modelo_escolhido}" not in modelos_disponiveis:
    print(f"⚠️ Modelo '{modelo_escolhido}' não encontrado. Alternando para 'gemini-pro'.")
    modelo_escolhido = "gemini-pro"

model = genai.GenerativeModel(modelo_escolhido)

# ============================================
# FUNÇÃO DE ANÁLISE DO SITE
# ============================================

def obter_html(url):
    """Faz o download do HTML do site."""
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.text
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return None


def analisar_site(url):
    """Analisa o conteúdo HTML usando o modelo Gemini."""
    html = obter_html(url)
    if not html:
        print("❌ Não foi possível obter o HTML.")
        return

    print(f"✅ HTML obtido com sucesso ({len(html)} caracteres).")

    try:
        prompt = (
            "Analise o código HTML a seguir e identifique potenciais riscos de segurança, "
            "links suspeitos, scripts maliciosos ou sinais de phishing:\n\n" + html
        )

        # Chamando o modelo de forma compatível com a versão 0.8.5
        response = model.generate_content(prompt)

        if hasattr(response, "text"):
            print("\n🧠 Análise do Gemini:\n")
            print(response.text)
        else:
            print("⚠️ Nenhum texto retornado pelo modelo.")
    except Exception as e:
        print(f"❌ Erro na chamada à API Gemini: {e}")
        print("❌ Não foi possível obter a análise.")


# ============================================
# EXECUÇÃO
# ============================================

if __name__ == "__main__":
    url = input("Digite a URL do site a ser analisado: ").strip()
    analisar_site(url)
