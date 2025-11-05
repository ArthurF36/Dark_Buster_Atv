import os
import random
import matplotlib.pyplot as plt
from collections import Counter
from openai import OpenAI
# from anthropic import Anthropic
# import google.generativeai as genai

# ==============================
# CONFIGURAÇÕES INICIAIS
# ==============================

# Escolha qual IA utilizar: "openai", "claude", "gemini"
IA_ATUAL = "openai"

# Caminho do arquivo de entrada
RESULTS_FILE = "/workspaces/Dark_Buster_Atv/Data/sites.txt"

# Verifica se o arquivo existe
if not os.path.exists(RESULTS_FILE):
    raise FileNotFoundError(f"Arquivo '{RESULTS_FILE}' não encontrado.")

# ==============================
# CARREGAMENTO DAS CHAVES DE API
# ==============================

# OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
client_openai = None
if openai_key:
    client_openai = OpenAI(api_key=openai_key)

# Anthropic (Claude)
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
client_claude = None
if anthropic_key:
    client_claude = Anthropic(api_key=anthropic_key)

# Gemini (Google)
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    genai.configure(api_key=google_key)

# ==============================
# FUNÇÕES DE ANÁLISE POR IA
# ==============================

def analisar_com_openai(texto):
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um analisador de padrões manipulativos em sites."},
            {"role": "user", "content": f"Analise o site e diga se ele contém design manipulativo: {texto}"}
        ]
    )
    return response.choices[0].message.content

def analisar_com_claude(texto):
    response = client_claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": f"Analise o site e diga se ele contém design manipulativo: {texto}"}]
    )
    return response.content[0].text

def analisar_com_gemini(texto):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Analise o site e diga se ele contém design manipulativo: {texto}")
    return response.text

def analisar_site(site):
    if IA_ATUAL == "openai" and client_openai:
        return analisar_com_openai(site)
    elif IA_ATUAL == "claude" and client_claude:
        return analisar_com_claude(site)
    elif IA_ATUAL == "gemini" and google_key:
        return analisar_com_gemini(site)
    else:
        raise EnvironmentError(f"❌ API key não configurada para {IA_ATUAL.upper()}")

# ==============================
# LEITURA DO ARQUIVO
# ==============================

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    sites = [linha.strip() for linha in f if linha.strip()]

print(f"\n🔍 Iniciando análise de {len(sites)} sites com {IA_ATUAL.upper()}...\n")

# ==============================
# SIMULAÇÃO DE ANÁLISE
# ==============================

data = []
padroes_disponiveis = ["Clickbait", "Pop-up", "Scroll for Action", "Urgency", "Misdirection"]
niveis_conf = ["alto", "medio", "baixo"]

for site in sites:
    print(f"➡️  Analisando: {site}")
    try:
        # Substitua esta linha pelo retorno real da IA quando desejar
        resultado_ia = analisar_site(site)

        manipulative = random.choice([True, False])
        resultado = {
            "manipulative_design": manipulative,
            "patterns_detected": [{"name": random.choice(padroes_disponiveis)} for _ in range(random.randint(1, 3))] if manipulative else [],
            "confidence_level": random.choice(niveis_conf)
        }
        data.append({"site": site, "resultado": resultado})
    except Exception as e:
        print(f"[ERRO] Falha na análise do site {site}: {e}")

# ==============================
# ANÁLISE GERAL
# ==============================

total_sites = len(data)
manipulative_sites = sum(1 for d in data if d["resultado"]["manipulative_design"])
non_manipulative_sites = total_sites - manipulative_sites

patterns = []
confidences = []
for d in data:
    res = d["resultado"]
    if res["manipulative_design"]:
        for p in res["patterns_detected"]:
            patterns.append(p["name"])
    confidences.append(res["confidence_level"])

# ==============================
# GERAÇÃO DOS GRÁFICOS
# ==============================

# 1️⃣ Gráfico 1 – Proporção de sites manipulativos
plt.figure(figsize=(6, 6))
plt.pie(
    [manipulative_sites, non_manipulative_sites],
    labels=["Com padrões manipulativos", "Sem padrões manipulativos"],
    autopct="%1.1f%%",
    startangle=90,
    colors=["#FF6666", "#66B2FF"]
)
plt.title(f"Distribuição de sites analisados ({IA_ATUAL.upper()})")
plt.show()

# 2️⃣ Gráfico 2 – Frequência dos padrões detectados
if patterns:
    contagem_padroes = Counter(patterns)
    plt.figure(figsize=(8, 5))
    plt.barh(list(contagem_padroes.keys()), list(contagem_padroes.values()), color="#FFB266")
    plt.xlabel("Quantidade de ocorrências")
    plt.ylabel("Tipo de padrão manipulativo")
    plt.title("Padrões manipulativos mais detectados")
    plt.tight_layout()
    plt.show()

# 3️⃣ Gráfico 3 – Distribuição de níveis de confiança
if confidences:
    contagem_conf = Counter(confidences)
    plt.figure(figsize=(6, 4))
    plt.bar(contagem_conf.keys(), contagem_conf.values(), color="#8FD14F")
    plt.xlabel("Nível de confiança")
    plt.ylabel("Quantidade de análises")
    plt.title("Distribuição dos níveis de confiança nas análises")
    plt.show()

# ==============================
# RESUMO FINAL
# ==============================

print("\n===== RELATÓRIO DARK BUSTER =====")
print(f"IA utilizada: {IA_ATUAL.upper()}")
print(f"Total de sites analisados: {total_sites}")
print(f"Com padrões manipulativos: {manipulative_sites}")
print(f"Sem padrões manipulativos: {non_manipulative_sites}")
if patterns:
    print(f"Padrões mais comuns: {', '.join([f'{p} ({n})' for p, n in Counter(patterns).most_common(5)])}")
if confidences:
    print(f"Níveis de confiança detectados: {dict(Counter(confidences))}")
print("=================================\n")
