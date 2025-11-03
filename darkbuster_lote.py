import matplotlib.pyplot as plt
from collections import Counter
import os

# ==============================
# CONFIGURAÇÕES
# ==============================

# Caminho do arquivo TXT
RESULTS_FILE = "/workspaces/Dark_Buster_Atv/Data/sites.txt"

# Verifica se o arquivo existe
if not os.path.exists(RESULTS_FILE):
    raise FileNotFoundError(f"Arquivo '{RESULTS_FILE}' não encontrado.")

# ==============================
# LEITURA DOS DADOS
# ==============================

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    sites = [linha.strip() for linha in f if linha.strip()]

# ==============================
# SIMULAÇÃO DE ANÁLISE (exemplo)
# ==============================
# Como não há JSON, vamos criar dados fictícios para padrões e níveis de confiança
# Para cada site, aleatoriamente decidimos se é manipulativo
import random

data = []
padroes_disponiveis = ["Clickbait", "Pop-up", "Scroll for Action", "Urgency", "Misdirection"]
niveis_conf = ["alto", "medio", "baixo"]

for site in sites:
    manipulative = random.choice([True, False])
    resultado = {}
    if manipulative:
        resultado["manipulative_design"] = True
        resultado["patterns_detected"] = [{"name": random.choice(padroes_disponiveis)} for _ in range(random.randint(1, 3))]
    else:
        resultado["manipulative_design"] = False
        resultado["patterns_detected"] = []
    resultado["confidence_level"] = random.choice(niveis_conf)
    data.append({"site": site, "resultado": resultado})

# ==============================
# ANÁLISE GERAL
# ==============================

total_sites = len(data)
manipulative_sites = sum(1 for d in data if d["resultado"]["manipulative_design"])
non_manipulative_sites = total_sites - manipulative_sites

# Coleta padrões detectados e níveis de confiança
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
plt.title("Distribuição de sites analisados")
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
else:
    print("Nenhum padrão manipulativo detectado para exibir no gráfico 2.")

# 3️⃣ Gráfico 3 – Distribuição de níveis de confiança
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

# ==============================
# RESUMO ESTATÍSTICO
# ==============================

print("\n===== RELATÓRIO DARK BUSTER =====")
print(f"Total de sites analisados: {total_sites}")
print(f"Com padrões manipulativos: {manipulative_sites}")
print(f"Sem padrões manipulativos: {non_manipulative_sites}")
if patterns:
    print(f"Padrões mais comuns: {', '.join([f'{p} ({n})' for p, n in Counter(patterns).most_common(5)])}")
if confidences:
    print(f"Níveis de confiança detectados: {dict(Counter(confidences))}")
print("=================================\n")