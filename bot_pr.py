import os
from dotenv import load_dotenv
import requests
import json

BOT_PATH = os.getenv("BOT_PATH")

# Caminho absoluto do diretório onde está o script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Carrega variáveis do .env no mesmo diretório do script
load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, ".env"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")
# Caminho absoluto para os arquivos
report_path = os.path.join(SCRIPT_DIR, "pr_report.txt")
description_path = os.path.join(SCRIPT_DIR, "pr_description.txt")

# Lê o diff salvo em pr_report.txt
with open(report_path, "r", encoding="utf-8") as f:
    diff = f.read()

prompt = """
Analise as alterações de código a seguir e gere um relatório detalhado seguindo EXATAMENTE este formato:

**Feature:** [Título resumido da funcionalidade ou alteração principal]

**Descrição:**
[Breve explicação do que foi implementado ou alterado]

**Resumo:**
[Resumo técnico das principais mudanças implementadas]

**Descrição do problema:**
[Contextualize o problema ou necessidade antes da alteração]

**Solução implementada:**
[Liste as principais mudanças técnicas:]
- ➕ [Para adições/criações]
- 🔧 [Para lógica de negócio/funções]
- 📦 [Para componentes/módulos]
- 🧪 [Para testes]
- 🛣️ [Para rotas/APIs]
- 📝 [Para configurações/documentação]
- 🎨 [Para melhorias de UI/UX]
- 🚀 [Para otimizações]

**Impacto Esperado:**
[Explique os benefícios, melhorias ou resultados esperados após a implementação]

Seja técnico, detalhado e mantenha EXATAMENTE esta estrutura em formato markdown.

Alterações de código:
""" + diff

def make_api_request(prompt_content):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "localhost",
        "X-Title": "bot_pr_script"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "Você é um assistente especializado em análise de código que gera relatórios detalhados para Pull Requests. Use formatação markdown e emojis moderadamente apenas nos itens das listas."
            },
            {"role": "user", "content": prompt_content}
        ],
        "max_tokens": 1000,
        "temperature": 0.3,
    }

    try:
        print("🚀 Enviando requisição para a API...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def process_response(response):
    if not response:
        return None
        
    if not response.content:
        print("❌ Resposta vazia da API!")
        print(f"Status code: {response.status_code}")
        return None

    try:
        data = response.json()
        if "choices" not in data or not data["choices"]:
            print("❌ Formato de resposta inválido")
            print(f"Resposta: {data}")
            return None
            
        return data["choices"][0]["message"]["content"].strip()
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        print(f"Conteúdo da resposta: {response.text}")
        return None

def save_result(summary):
    try:
        with open(description_path, "w", encoding="utf-8") as f:
            f.write(summary)
        print("✅ Resumo gerado e salvo em pr_description.txt")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False

def show_preview(summary):
    print("\n" + "="*60)
    print("📋 PREVIEW DO RELATÓRIO GERADO")
    print("="*60)
    print(summary)
    print("="*60 + "\n")

def main():
    print("🤖 Iniciando geração de relatório de PR...")
    
    # Verificar se o arquivo de diff existe
    if not os.path.exists(report_path):
        print(f"❌ Arquivo {report_path} não encontrado!")
        return
    
    # Fazer requisição para a API do OpenRouter
    response = make_api_request(prompt)
    
    # Processar resposta da API do OpenRouter
    summary = process_response(response)
    
    if not summary:
        print("❌ Falha ao gerar o relatório")
        return
    
    # Exibir preview
    show_preview(summary)
    
    # Salvar resultado
    if save_result(summary):
        print("🎉 Processo concluído com sucesso!")
    else:
        print("❌ Falha ao salvar o arquivo")

if __name__ == "__main__":
    main()
