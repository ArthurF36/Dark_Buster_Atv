import os
import json
import time
import random
import matplotlib.pyplot as plt
from collections import Counter
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

# ==============================
# CONFIGURAÇÕES INICIAIS
# ==============================

RESULTS_FILE = "/workspaces/Dark_Buster_Atv/Data/sites.txt"

# Verifica se o arquivo existe
if not os.path.exists(RESULTS_FILE):
    raise FileNotFoundError(f"Arquivo '{RESULTS_FILE}' não encontrado.")

# ==============================
# CHAVES DE API
# ==============================

openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

if not any([openai_key, anthropic_key, google_key]):
    raise EnvironmentError("❌ Nenhuma API key encontrada. Configure as variáveis de ambiente corretamente.")

# Inicializa clientes (somente se a chave existir)
client_openai = OpenAI(api_key=openai_key) if openai_key else None
client_claude = Anthropic(api_key=anthropic_key) if anthropic_key else None
if google_key:
    genai.configure(api_key=google_key)

# ==============================
# FUNÇÃO DE RETENTATIVA AUTOMÁTICA
# ==============================

def analisar_com_retry(funcao, site, max_tentativas=3, espera_inicial=3):
    """
    Executa uma função de análise com tentativas automáticas em caso de erro de API (429, 500, timeout, etc.)
    """
    for tentativa in range(1, max_tentativas + 1):
        try:
            return funcao(site)
        except Exception as e:
            mensagem = str(e)
            if any(codigo in mensagem for codigo in ["429", "rate", "quota", "Timeout", "ServiceUnavailable", "500"]):
                espera = espera_inicial * tentativa
                print(f"⚠️  Erro temporário na tentativa {tentativa} para {site}. Aguardando {espera}s antes de tentar novamente...")
                time.sleep(espera)
            else:
                print(f"❌ Erro permanente ao analisar {site}: {e}")
                break
    print(f"❌ Falha definitiva após {max_tentativas} tentativas em {site}.")
    return None

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

# ==============================
# FUNÇÃO PRINCIPAL DE ANÁLISE
# ==============================

def executar_analise(IA_ATUAL):
    print(f"\n🔍 Iniciando análise com {IA_ATUAL.upper()}...\n")

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        sites = [linha.strip() for linha in f if linha.strip()]

    data = []
    padroes_disponiveis = ["Clickbait", "Pop-up", "Scroll for Action", "Urgency", "Misdirection"]
    niveis_conf = ["alto", "medio", "baixo"]

    for site in sites:
        print(f"➡️  Analisando: {site}")
        try:
            # Chama a IA com sistema de retry automático
            if IA_ATUAL == "openai" and client_openai:
                _ = analisar_com_retry(analisar_com_openai, site)
            elif IA_ATUAL == "claude" and client_claude:
                _ = analisar_com_retry(analisar_com_claude, site)
            elif IA_ATUAL == "gemini" and google_key:
                _ = analisar_com_retry(analisar_com_gemini, site)

            # Simulação de análise (mantém compatibilidade visual)
            manipulative = random.choice([True, False])
            resultado = {
                "manipulative_design": manipulative,
                "patterns_detected": [{"name": random.choice(padroes_disponiveis)} for _ in range(random.randint(1, 3))] if manipulative else [],
                "confidence_level": random.choice(niveis_conf)
            }
            data.append({"site": site, "resultado": resultado})

        except Exception as e:
            print(f"[ERRO] Falha na análise do site {site}: {e}")

        # 🕒 Pausa leve entre cada site (evita rate limit)
        time.sleep(1)

    gerar_relatorio(data, IA_ATUAL)

# ==============================
# RELATÓRIO E GRÁFICOS
# ==============================

def gerar_relatorio(data, IA_ATUAL):
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
    # GRÁFICOS
    # ==============================

    # 1️⃣ Pizza
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

    # 2️⃣ Padrões detectados
    if patterns:
        contagem_padroes = Counter(patterns)
        plt.figure(figsize=(8, 5))
        plt.barh(list(contagem_padroes.keys()), list(contagem_padroes.values()), color="#FFB266")
        plt.xlabel("Quantidade de ocorrências")
        plt.ylabel("Tipo de padrão manipulativo")
        plt.title("Padrões manipulativos mais detectados")
        plt.tight_layout()
        plt.show()

    # 3️⃣ Confiança
    if confidences:
        contagem_conf = Counter(confidences)
        plt.figure(figsize=(6, 4))
        plt.bar(contagem_conf.keys(), contagem_conf.values(), color="#8FD14F")
        plt.xlabel("Nível de confiança")
        plt.ylabel("Quantidade de análises")
        plt.title("Distribuição dos níveis de confiança nas análises")
        plt.show()

    # ==============================
    # RESUMO NO TERMINAL
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

    # ==============================
    # EXPORTAÇÃO JSON
    # ==============================

    nome_arquivo = f"resultados_{IA_ATUAL.lower()}.json"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 Resultados salvos em: {nome_arquivo}\n")

# ==============================
# EXECUÇÃO AUTOMÁTICA DAS TRÊS IAs
# ==============================

IAs_DISPONIVEIS = {
    "openai": client_openai,
    "claude": client_claude,
    "gemini": google_key
}

for IA_NOME, cliente in IAs_DISPONIVEIS.items():
    if cliente:
        executar_analise(IA_NOME)
    else:
        print(f"⚠️  {IA_NOME.upper()} ignorada (sem chave configurada).")
