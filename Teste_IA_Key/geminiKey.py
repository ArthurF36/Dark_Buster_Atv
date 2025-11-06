import os

# Verifica se a variável está configurada
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print("✅ GEMINI_API_KEY foi detectada no ambiente!")
    print(f"Tamanho da chave: {len(api_key)} caracteres")
    print(f"Prefixo (seguro): {api_key[:7]}************")
else:
    print("❌ GEMINI_API_KEY não foi encontrada. Verifique se o secret foi configurado corretamente.")