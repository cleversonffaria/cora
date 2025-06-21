import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.constants import *

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv(API_KEY_VAR)
        self.api_base_url = os.getenv(API_BASE_URL_VAR)
        self.model = os.getenv(MODEL_VAR)
        
        client_kwargs = {"api_key": self.api_key}
        if self.api_base_url:
            client_kwargs["base_url"] = self.api_base_url
        
        self.client = OpenAI(**client_kwargs)
    
    def is_configured(self):
        return bool(self.api_key)
    
    def get_suggestion(self, prompt, model=None, temperature=DEFAULT_TEMPERATURE):
        if model is None:
            model = self.model
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            return response.choices[0].message.content.strip().replace("`", "")
        except Exception as e:
            print(f"❌ Error with AI API: {e}")
            exit(1)
    
    def generate_commit_message(self, diff, temperature=DEFAULT_TEMPERATURE, history=None):
        prompt = (
            "You are an assistant that generates commit messages in the conventional commits format.\n"
            "Based on the git diff below, identify the MOST SIGNIFICANT change and generate a short, clear commit message in English about it.\n"
            "Focus on the main purpose of the change.\n"
            "Use prefixes like feat, fix, chore, refactor, test, docs, style, perf, ci, build, revert etc.\n"
            "Only the message, with no extra explanations or remarks.\n"
            "Generate ONLY ONE commit message, with no line breaks or special formatting.\n"
            "Nothing but a commit message."
        )
        if history:
            history_prompt = "\n\nCrucially, provide a different and unique suggestion from the ones I have already rejected:\n- "
            history_prompt += "\n- ".join(history)
            prompt += history_prompt

        prompt += f"\n\nDiff:\n{diff}"
        return self.get_suggestion(prompt, temperature=temperature)
    
    def generate_branch_name(self, diff, temperature=DEFAULT_BRANCH_TEMPERATURE, history=None):
        prompt = (
            "You are an assistant that generates Git branch names.\n"
            "Based on the git diff below, identify the MOST SIGNIFICANT change and generate a short, descriptive branch name in English for it, "
            "using hyphens to separate words and following the 'type/short-description' format.\n"
            "The name should reflect the main purpose of the changes.\n"
            "Use prefixes like feat/, fix/, chore/, refactor/, test/, docs/, style/, perf/, ci/, build/, revert/.\n"
            "Examples: feat/add-user-login, fix/resolve-payment-bug, chore/update-dependencies.\n"
            "Generate ONLY the branch name, with no extra explanations or remarks."
        )
        if history:
            history_prompt = "\n\nCrucially, provide a different and unique suggestion from the ones I have already rejected:\n- "
            history_prompt += "\n- ".join(history)
            prompt += history_prompt

        prompt += f"\n\nDiff:\n{diff}"
        return self.get_suggestion(prompt, temperature=temperature)
    
    def generate_pr_description(self, diff):
        print("🤖 Gerando descrição do PR...")
        
        prompt = f"""
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
{diff}
"""
        
        return self.get_suggestion(prompt, temperature=0.3) 