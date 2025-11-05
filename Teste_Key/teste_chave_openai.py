import os

# Verifica se a variável está configurada
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ OPENAI_API_KEY foi detectada no ambiente!")
    print(f"Tamanho da chave: {len(api_key)} caracteres")
    print(f"Prefixo (seguro): {api_key[:7]}************")
else:
    print("❌ OPENAI_API_KEY não foi encontrada. Verifique se o secret foi configurado corretamente.")