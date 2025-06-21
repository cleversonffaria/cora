#!/usr/bin/env python3

import subprocess
import os
import argparse
import sys
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
from constants import *

load_dotenv()

# Get API configuration from environment
API_KEY = os.getenv(API_KEY_VAR)
API_BASE_URL = os.getenv(API_BASE_URL_VAR)
MODEL = os.getenv(MODEL_VAR)

# Initialize client with dynamic configuration
client_kwargs = {"api_key": API_KEY}
if API_BASE_URL:
    client_kwargs["base_url"] = API_BASE_URL

client = OpenAI(**client_kwargs)

def show_version():
    print(f"🤖 {COMMAND_NAME.title()} v{VERSION}")
    print("Assistente de fluxo de trabalho Git com IA")
    print(REPOSITORY_URL)

def show_welcome():
    print(f"""
🤖 {MESSAGES["WELCOME_TITLE"].format(command_name=COMMAND_NAME.title(), version=VERSION)}

✨ {MESSAGES["WELCOME_SUBTITLE"]}

🚀 {COMMAND_NAME.title()} ajuda você a:
   • Gerar mensagens de commit profissionais automaticamente
   • Criar nomes de branches descritivos e organizados  
   • Automatizar seu fluxo de trabalho Git completo
   • Economizar tempo e manter consistência no projeto

💡 Para começar:
   {COMMAND_NAME} --help          # Ver todas as opções disponíveis
   {COMMAND_NAME} -c              # Gerar e fazer commit
   {COMMAND_NAME} -b -c --pr      # Fluxo completo: branch + commit + PR

🔑 Não esqueça de configurar sua chave da API no arquivo .env!
""")

def show_help():
    print(f"""🤖 {COMMAND_NAME.title()} v{VERSION} - Assistente de Git com IA

{HELP_SECTIONS["USAGE"]}
  {COMMAND_NAME} [OPÇÕES]

{HELP_SECTIONS["OPTIONS"]}
  -b, --branch         Cria uma nova branch
  -c, --commit         Gera e executa commit
  --pr                 {OPTION_DESCRIPTIONS["PR"]}
  -v, --version        {OPTION_DESCRIPTIONS["VERSION"]}
  --help               {OPTION_DESCRIPTIONS["HELP"]}

{HELP_SECTIONS["EXAMPLES"]}
  {COMMAND_NAME} -c                 # Gera apenas commit
  {COMMAND_NAME} -b                 # Cria apenas branch
  {COMMAND_NAME} -b -c              # Cria branch + commit
  {COMMAND_NAME} -c --pr           # Commit + abre PR
  {COMMAND_NAME} -b -c --pr        # Fluxo completo: branch + commit + PR

{HELP_SECTIONS["SETUP"]}
  Configure sua chave da API no arquivo .env:
  {API_KEY_VAR}="sua_chave_aqui"
  {MODEL_VAR}="modelo_desejado"
  {API_BASE_URL_VAR}="url_da_api"

{HELP_SECTIONS["NOTE"]}
  O comando automaticamente adiciona todas as mudanças (git add .) antes de gerar sugestões.
""")

def run_git_command(command, check=True):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {' '.join(command)}")
        print(f"  {e.stderr.strip()}")
        exit(1)
    except FileNotFoundError:
        print(f"❌ git command not found. Please ensure Git is installed and in your PATH.")
        exit(1)

def get_git_diff():
    run_git_command(["git", "add", "."])
    diff = run_git_command(["git", "diff", "--cached"])
    return diff

def get_ai_suggestion(prompt, model=None, temperature=DEFAULT_TEMPERATURE):
    if model is None:
        model = MODEL
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip().replace("`", "")
    except Exception as e:
        print(f"❌ Error with AI API: {e}")
        exit(1)

def generate_commit_message(diff, temperature=DEFAULT_TEMPERATURE, history=None):
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
    return get_ai_suggestion(prompt, temperature=temperature)

def generate_branch_name(diff, temperature=DEFAULT_BRANCH_TEMPERATURE, history=None):
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
    return get_ai_suggestion(prompt, temperature=temperature)

def user_interaction_loop(prompt_question, generation_function, diff):
    if "branch" in prompt_question.lower():
        suggested_temperature = DEFAULT_BRANCH_TEMPERATURE
    else:
        suggested_temperature = DEFAULT_TEMPERATURE

    previous_suggestions = []
    while True:
        suggestion = generation_function(
            diff,
            temperature=suggested_temperature,
            history=previous_suggestions
        )
        print(f"\n💬 {prompt_question}:\n{suggestion}")

        response = input("    ➡️ Accept? (Y) | 🔄 Regenerate? (r) | 🚫 Cancel? (n): ").strip().lower()

        if response in ('y', ''):
            return suggestion
        elif response == "r":
            if suggestion:
                previous_suggestions.append(suggestion)
            suggested_temperature = min(1.0, suggested_temperature + 0.2)
            print(f"ℹ️ Trying a different suggestion (temperature: {suggested_temperature:.1f})...")
            continue
        else:
            return None

def open_in_browser(url):
    command = []
    if sys.platform.startswith('linux'):
        command = ['xdg-open', url]
    elif sys.platform == 'darwin':
        command = ['open', url]
    elif sys.platform == 'win32':
        command = ['start', url]
    
    if not command:
        return False

    try:
        # Usamos DEVNULL para suprimir qualquer saída do comando
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_pr_description(base_branch, current_branch):
    """Gera descrição detalhada do PR usando IA baseado no diff"""
    print("🤖 Gerando descrição do PR...")
    
    # Gera diff entre as branches
    try:
        diff = run_git_command(["git", "diff", f"{base_branch}..{current_branch}"])
        if not diff:
            print("⚠️ Nenhuma diferença encontrada entre as branches.")
            return None
    except:
        print("❌ Erro ao gerar diff entre branches.")
        return None
    
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
    
    return get_ai_suggestion(prompt, temperature=0.3)

def check_github_cli():
    """Verifica se GitHub CLI está instalado e autenticado"""
    try:
        # Verifica se gh está instalado
        run_git_command(["gh", "--version"])
        
        # Verifica se está autenticado
        run_git_command(["gh", "auth", "status"])
        
        # Verifica se consegue acessar o repositório
        run_git_command(["gh", "repo", "view"])
        
        return True
    except:
        return False

def create_pr_with_cli(base_branch, current_branch, description):
    """Cria PR usando GitHub CLI"""
    try:
        title = f'"PR: {current_branch} to {base_branch}"'
        
        # Cria arquivo temporário com a descrição
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(description)
            temp_file_path = temp_file.name
        
        # Cria o PR usando --body-file
        pr_url = run_git_command([
            "gh", "pr", "create", 
            "--base", base_branch,
            "--title", title,
            "--body-file", temp_file_path
        ])
        
        # Remove arquivo temporário
        os.unlink(temp_file_path)
        
        return pr_url.strip()
    except Exception as e:
        # Remove arquivo temporário em caso de erro
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
            
        error_msg = str(e)
        if "must be a collaborator" in error_msg:
            print("⚠️ Você não tem permissão de colaborador neste repositório.")
            print("   Continuando com método alternativo...")
        elif "uncommitted changes" in error_msg:
            print("⚠️ Há alterações não commitadas.")
            print("   Faça commit das alterações antes de criar o PR.")
        else:
            print(f"❌ Erro ao criar PR: {e}")
        return None

def get_current_branch():
    """Retorna a branch atual"""
    try:
        return run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    except:
        return None

def get_local_branches():
    """Retorna lista de branches locais, excluindo as com '/'"""
    try:
        branches_output = run_git_command(["git", "branch", "--list"])
        branches = []
        for line in branches_output.split('\n'):
            branch = line.strip().replace('*', '').strip()
            if branch and '/' not in branch:
                branches.append(branch)
        return branches
    except:
        return []

def get_pr_url(branch_name):
    try:
        remote_url = run_git_command(["git", "config", "--get", "remote.origin.url"])
        if not remote_url:
            return None

        if remote_url.startswith("https://"):
            repo_path = remote_url.replace("https://github.com/", "").replace(".git", "")
        elif remote_url.startswith("git@"):
            repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
        else:
            return None

        return f"https://github.com/{repo_path}/pull/new/{branch_name}"
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser(description="Assistente de fluxo de trabalho Git com IA", add_help=False)
    parser.add_argument("--branch", "-b", action="store_true", help="Cria uma nova branch")
    parser.add_argument("--commit", "-c", action="store_true", help="Gera e executa commit")
    parser.add_argument("--pr", action="store_true", help=OPTION_DESCRIPTIONS["PR"])
    parser.add_argument("--version", "-v", "--v", "-version", action="store_true", help=OPTION_DESCRIPTIONS["VERSION"])
    parser.add_argument("--help", action="store_true", help=OPTION_DESCRIPTIONS["HELP"])
    args = parser.parse_args()

    # Handle help and version first
    if args.help:
        show_help()
        return
    
    if args.version:
        show_version()
        return

    if not any([args.branch, args.commit, args.pr]):
        show_welcome()
        return

    if args.branch or args.commit:
        if not API_KEY:
            print(MESSAGES["API_KEY_NOT_SET"])
            print(MESSAGES["API_KEY_HELP"])
            exit(1)

        diff = get_git_diff()

        if not diff:
            print(MESSAGES["NO_CHANGES"])
            exit(0)

    # Store original branch for potential rollback
    original_branch_name = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    branch_name = None
    new_branch_created = False

    # 1. Handle branch creation
    if args.branch:
        print("🌿 Creating new branch...")
        branch_name = user_interaction_loop("Suggested branch name", generate_branch_name, diff)
        if branch_name:
            if branch_name == original_branch_name:
                print(f"⚠️ The suggested branch ('{branch_name}') is the same as the current branch. No new branch will be created.")
            else:
                print(f"🌿 Creating and checking out branch '{branch_name}'...")
                run_git_command(["git", "checkout", "-b", branch_name], check=False)
                current_branch_check = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
                if current_branch_check == branch_name:
                    new_branch_created = True
                    print(f"✅ Switched to new branch '{branch_name}'.")
                else:
                    print(f"⚠️ Could not create or switch to branch '{branch_name}'. Check if it already exists or if there are conflicts.")
                    print(f"   Continuing on branch '{original_branch_name}'.")
                    branch_name = None
        else:
            print("🚫 Branch creation canceled.")
            return

    # 2. Handle commit creation
    if args.commit:
        print("📝 Creating commit...")
        commit_message = user_interaction_loop("Suggested commit message", generate_commit_message, diff)
        
        if commit_message:
            current_branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            print(f"\n📝 Commit Review:")
            print(f"   Message: \"{commit_message}\"")
            print(f"   Branch: {current_branch}")

            # Always create the commit first
            print("\n💾 Creating commit...")
            run_git_command(["git", "commit", "-m", commit_message])
            print("✅ Commit created successfully!")

            # Ask about push
            push_confirmation = input(f"\n🚀 Push to remote branch '{current_branch}'? (Y/n): ").strip().lower()
            
            if push_confirmation in ('y', ''):
                print(f"🚀 Pushing to branch '{current_branch}'...")
                if new_branch_created:
                    run_git_command(["git", "push", "--set-upstream", "origin", current_branch])
                else:
                    run_git_command(["git", "push", "origin", current_branch])
                
                print("✨ Push successful!")
            else:
                print("ℹ️ Commit created locally. Push skipped.")
                print(f"   To push later, run: git push origin {current_branch}")
        else:
            print("🚫 Commit canceled.")
            return

    # 3. Handle PR creation
    if args.pr:
        print("📋 Iniciando processo de criação de Pull Request...")
        
        # Get current branch
        current_branch = get_current_branch()
        if not current_branch:
            print("❌ Não foi possível obter a branch atual.")
            return
        
        # Get branches for comparison
        branches = get_local_branches()
        if not branches:
            print("❌ Nenhuma branch disponível para comparação.")
            return
        
        # Filter out current branch
        available_branches = [b for b in branches if b != current_branch]
        if not available_branches:
            print("❌ Nenhuma branch base disponível para comparação.")
            return
        
        print(f"📍 Branch atual: {current_branch}")
        print("\n📋 Selecione a branch base para comparação:")
        
        for i, branch in enumerate(available_branches, 1):
            print(f"{i}. {branch}")
        
        try:
            choice = int(input("\n🔢 Digite o número da branch: "))
            if 1 <= choice <= len(available_branches):
                base_branch = available_branches[choice - 1]
                print(f"✅ Comparando {current_branch} com {base_branch}")
                
                # Gera descrição com IA se API_KEY estiver disponível
                description = None
                if API_KEY:
                    description = generate_pr_description(base_branch, current_branch)
                
                if not description:
                    description = f"PR automático: {current_branch} to {base_branch}"
                
                # Sempre mostra a descrição primeiro
                if description:
                    print("\n\n" + "="*70)
                    print("📋 DESCRIÇÃO DO PULL REQUEST")
                    print("="*70)
                    print(f"TÍTULO: PR: {current_branch} to {base_branch}")
                    print(f"BASE: {base_branch}")
                    print(f"HEAD: {current_branch}")
                    print("="*70)
                    print("DESCRIÇÃO:")
                    print()
                    print(description)
                    print()
                    print("="*70 + "\n\n")
                
                # Verifica se GitHub CLI está disponível e tenta criar PR
                github_cli_available = check_github_cli()
                pr_created_successfully = False
                
                if github_cli_available:
                    print("✅ GitHub CLI autenticado. Tentando criar PR automaticamente...")
                    
                    # Cria PR automaticamente
                    pr_url = create_pr_with_cli(base_branch, current_branch, description)
                    if pr_url:
                        print(f"🎉 PR criado com sucesso!")
                        print(f"🔗 URL: {pr_url}")
                        pr_created_successfully = True
                    else:
                        print("❌ Não foi possível criar o PR automaticamente.")
                        print("   Continuando com método manual...")
                else:
                    print("⚠️ GitHub CLI não disponível ou não autenticado.")
                    print("   Continuando com método manual...")
                
                # SEMPRE abre no navegador se não criou automaticamente
                if not pr_created_successfully:
                    pr_url = get_pr_url(current_branch)
                    if pr_url:
                        print("🚀 Abrindo PR no navegador...")
                        if not open_in_browser(pr_url):
                            print(f"⚠️ Não foi possível abrir o navegador automaticamente.")
                            print(f"   Copie e cole esta URL:\n   {pr_url}")
                        else:
                            print("✅ PR aberto no navegador!")
                    else:
                        print("⚠️ Não foi possível gerar URL do PR. Verifique se há um remote GitHub válido.")
                    
            else:
                print("❌ Opção inválida.")
        except ValueError:
            print("❌ Por favor, digite um número válido.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{MESSAGES['OPERATION_CANCELLED']}")
        exit(130)
