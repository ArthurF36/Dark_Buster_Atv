# ===========================================
# DARK BUSTER – MVP com IA Generativa (GPT)
# Compatível com openai >= 1.0.0
# ===========================================

import os
import json
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from collections import Counter
from openai import OpenAI

# ===========================================
# CONFIGURAÇÕES
# ===========================================

# Obtém chave da variável de ambiente para o IA openai
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError(
        "❌ Variável de ambiente OPENAI_API_KEY não encontrada.\n"
        "Defina sua chave com:\n"
        "   export OPENAI_API_KEY='sua_chave_aqui' (Linux/macOS)\n"
        "ou setx OPENAI_API_KEY 'sua_chave_aqui' (Windows)"
    )

client = OpenAI(api_key=api_key)
RESULTS_FILE = "/workspaces/Dark_Buster_Atv/Data/sites.txt"

if not os.path.exists(RESULTS_FILE):
    raise FileNotFoundError(f"Arquivo '{RESULTS_FILE}' não encontrado.")

# Prompt interno (retirado do Dark Buster.pdf)
ANALYSIS_PROMPT = """
Você é um sistema de verificação automática de padrões de design manipulativo em websites (dark patterns).

Sua tarefa é analisar o conteúdo de um site (HTML, textos, scripts e layout descrito) e identificar se ele contém padrões manipulativos.

Responda sempre em JSON estruturado no seguinte formato:
{
  "manipulative_design": true/false,
  "patterns_detected": [
    { "name": "Nome do padrão", "description": "Breve descrição do padrão encontrado" }
  ],
  "confidence_level": "alta/média/baixa"
}

Regras de análise:
1. Identifique se o site contém ou não padrões manipulativos.
2. Se encontrar, descreva cada padrão de forma clara e breve.
3. Sempre inclua um nível de confiança (alta, média ou baixa).
4. Se não houver manipulação clara, retorne "manipulative_design": false.
Sua saída deve ser somente o JSON.
"""

# ===========================================
# FUNÇÕES PRINCIPAIS
# ===========================================

def fetch_html(url: str) -> str:
    """Baixa o HTML de uma URL e retorna o conteúdo como texto."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[ERRO] Falha ao acessar {url}: {e}")
        return ""

def analyze_site_with_ai(url: str) -> dict:
    """Envia o HTML e o prompt para a IA generativa e retorna a análise JSON."""
    html = fetch_html(url)
    if not html:
        return {"site": url, "erro": "HTML não obtido"}

    user_prompt = f"{ANALYSIS_PROMPT}\n\nConteúdo do site:\n{html[:12000]}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um analisador de padrões manipulativos em websites."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800
        )
        result_text = response.choices[0].message.content[0].text.strip()

        try:
            result_json = json.loads(result_text)
        except json.JSONDecodeError:
            print(f"[AVISO] Resposta não veio como JSON válido para {url}.")
            return {"site": url, "raw_response": result_text}

        return {"site": url, "resultado": result_json}

    except Exception as e:
        print(f"[ERRO] Falha na chamada à API para {url}: {e}")
        return {"site": url, "erro": str(e)}

# ===========================================
# EXECUÇÃO PRINCIPAL
# ===========================================

def main():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        sites = [linha.strip() for linha in f if linha.strip()]

    data = []
    print(f"\n🔍 Iniciando análise de {len(sites)} sites...\n")

    for site in sites:
        print(f"➡️  Analisando: {site}")
        result = analyze_site_with_ai(site)
        data.append(result)

    # Salva resultados em JSON local
    with open("resultado_darkbuster.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # =======================================
    # ANÁLISE E VISUALIZAÇÃO DOS RESULTADOS
    # =======================================

    valid_results = [d for d in data if "resultado" in d]
    if not valid_results:
        print("Nenhum resultado válido retornado pela IA.")
        return

    total_sites = len(valid_results)
    manipulative_sites = sum(1 for d in valid_results if d["resultado"].get("manipulative_design"))
    non_manipulative_sites = total_sites - manipulative_sites

    patterns = []
    confidences = []

    for d in valid_results:
        res = d["resultado"]
        if res.get("manipulative_design"):
            for p in res.get("patterns_detected", []):
                patterns.append(p["name"])
        conf = res.get("confidence_level")
        if conf:
            confidences.append(conf.lower())

    # ============================
    # GRÁFICOS
    # ============================

    # 1️⃣ Proporção de sites manipulativos
    plt.figure(figsize=(6, 6))
    plt.pie(
        [manipulative_sites, non_manipulative_sites],
        labels=["Com padrões manipulativos", "Sem padrões manipulativos"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#FF6666", "#66B2FF"]
    )
    plt.title("Distribuição de sites analisados")
    plt.show()

    # 2️⃣ Frequência dos padrões detectados
    if patterns:
        contagem_padroes = Counter(patterns)
        plt.figure(figsize=(8, 5))
        plt.barh(list(contagem_padroes.keys()), list(contagem_padroes.values()), color="#FFB266")
        plt.xlabel("Quantidade de ocorrências")
        plt.ylabel("Tipo de padrão manipulativo")
        plt.title("Padrões manipulativos mais detectados")
        plt.tight_layout()
        plt.show()
    else:
        print("Nenhum padrão manipulativo detectado para exibir no gráfico 2.")

    # 3️⃣ Distribuição dos níveis de confiança
    if confidences:
        contagem_conf = Counter(confidences)
        plt.figure(figsize=(6, 4))
        plt.bar(contagem_conf.keys(), contagem_conf.values(), color="#8FD14F")
        plt.xlabel("Nível de confiança")
        plt.ylabel("Quantidade de análises")
        plt.title("Distribuição dos níveis de confiança nas análises")
        plt.show()
    else:
        print("Nenhum nível de confiança encontrado para exibir no gráfico 3.")

    # ============================
    # RELATÓRIO FINAL
    # ============================
    print("\n===== RELATÓRIO DARK BUSTER =====")
    print(f"Total de sites analisados: {total_sites}")
    print(f"Com padrões manipulativos: {manipulative_sites}")
    print(f"Sem padrões manipulativos: {non_manipulative_sites}")
    if patterns:
        print(f"Padrões mais comuns: {', '.join([f'{p} ({n})' for p, n in Counter(patterns).most_common(5)])}")
    if confidences:
        print(f"Níveis de confiança detectados: {dict(Counter(confidences))}")
    print("=================================\n")

# ===========================================
# EXECUTAR
# ===========================================
if __name__ == "__main__":
    main()
