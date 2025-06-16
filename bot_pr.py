import os
from dotenv import load_dotenv
import requests

BOT_PATH = os.getenv("BOT_PATH")

# Caminho absoluto do diretório onde está o script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Carrega variáveis do .env no mesmo diretório do script
load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, ".env"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")
# Caminho absoluto para os arquivos
relatorio_path = os.path.join(SCRIPT_DIR, "relatorio_pr.txt")
descricao_path = os.path.join(SCRIPT_DIR, "descricao_pr.txt")

# Lê o diff salvo em relatorio_pr.txt
with open(relatorio_path, "r") as f:
    diff = f.read()

prompt = (
    "Analise as alterações de código a seguir e gere um relatório detalhado no seguinte formato:\n\n"
    "Feature: [Título resumido da funcionalidade ou alteração principal]\n"
    "Resumo: [Breve explicação do que foi implementado ou alterado]\n"
    "Descrição do problema: [Contextualize o problema ou necessidade antes da alteração]\n"
    "Solução implementada: [Liste e explique as principais mudanças técnicas, como novas rotas, métodos, entidades, lógica de negócio, validações, etc. Use subtópicos ou marcadores se necessário]\n"
    "Impacto esperado: [Explique os benefícios, melhorias ou resultados esperados após a implementação]\n\n"
    "Seja claro, objetivo, técnico e siga sempre essa estrutura.\n\n"
    "Alterações de código:\n"
    f"{diff}"
)


headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "localhost",
    "X-Title": "bot_pr_script"
}

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "Você é um assistente que resume alterações de código para Pull Requests."},
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 500,
    "temperature": 0.3,
}

# 1. Faça a requisição
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json=payload,
    timeout=60
)

# 2. Cheque se a resposta está vazia
if not response.content:
    print("Resposta vazia da API!")
    print("Status code:", response.status_code)
    exit(1)

# 3. Tente decodificar o JSON
try:
    data = response.json()
except Exception as e:
    print("Erro ao decodificar JSON:", e)
    print("Conteúdo da resposta:", response.text)
    exit(1)

# 4. Processe o resultado normalmente
resumo = data["choices"][0]["message"]["content"].strip()

# Salva o resumo em descricao_pr.txt
with open(descricao_path, "w") as f:
    f.write(resumo)

print("Resumo gerado salvo em descricao_pr.txt")
