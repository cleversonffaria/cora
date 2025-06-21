#!/usr/bin/env python3

import subprocess
import os
import argparse
import sys
from openai import OpenAI
from dotenv import load_dotenv
from constants import *

load_dotenv()

# Get API configuration from environment
API_KEY = os.getenv(API_KEY_VAR)
API_BASE_URL = os.getenv(API_BASE_URL_VAR)
MODEL = os.getenv(MODEL_VAR, DEFAULT_MODEL)

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
   {COMMAND_NAME} -b              # {EXAMPLE_DESCRIPTIONS["BRANCH_COMMIT"]}
   {COMMAND_NAME} -b --pr         # {EXAMPLE_DESCRIPTIONS["FULL_WORKFLOW"]}

🔑 Não esqueça de configurar sua chave da API no arquivo .env!
""")

def show_help():
    print(f"""🤖 {COMMAND_NAME.title()} v{VERSION} - Assistente de Git com IA

{HELP_SECTIONS["USAGE"]}
  {COMMAND_NAME} [OPÇÕES]

{HELP_SECTIONS["OPTIONS"]}
  -b, --branch         {OPTION_DESCRIPTIONS["BRANCH"]}
  --pr                 {OPTION_DESCRIPTIONS["PR"]}
  -v, --version        {OPTION_DESCRIPTIONS["VERSION"]}
  --help               {OPTION_DESCRIPTIONS["HELP"]}

{HELP_SECTIONS["EXAMPLES"]}
  {COMMAND_NAME}                    # {EXAMPLE_DESCRIPTIONS["COMMIT_ONLY"]}
  {COMMAND_NAME} -b                 # {EXAMPLE_DESCRIPTIONS["BRANCH_COMMIT"]}
  {COMMAND_NAME} -b --pr           # {EXAMPLE_DESCRIPTIONS["FULL_WORKFLOW"]}

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
    parser.add_argument("--branch", "-b", action="store_true", help=OPTION_DESCRIPTIONS["BRANCH"])
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

    # Check if no arguments were provided (only default values)
    if not any([args.branch, args.pr]):
        show_welcome()
        return

    if not API_KEY:
        print(MESSAGES["API_KEY_NOT_SET"])
        print(MESSAGES["API_KEY_HELP"])
        exit(1)

    diff = get_git_diff()

    if not diff:
        print(MESSAGES["NO_CHANGES"])
        exit(0)

    branch_name = None
    new_branch_created = False
    original_branch_name = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])

    if args.branch:
        branch_name = user_interaction_loop("Suggested branch name", generate_branch_name, diff)
        if branch_name:
            if branch_name == original_branch_name:
                print(f"⚠️ The suggested branch ('{branch_name}') is the same as the current branch. No new branch will be created.")
                new_branch_created = False
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
            print("🚫 Branch creation canceled. Continuing on the current branch.")

    commit_message = user_interaction_loop("Suggested commit message", generate_commit_message, diff)

    if commit_message:
        print(f"\n📝 Commit Review:")
        print(f"   Message: \"{commit_message}\"")

        branch_to_commit_on = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        if new_branch_created and branch_name:
            print(f"   Branch: {branch_name} (new)")
        else:
            print(f"   Branch: {branch_to_commit_on} (current)")

        confirmation = input("\n✅ Proceed with commit and push? (Y/n): ").strip().lower()

        if confirmation in ('y', ''):
            print("💾 Committing...")
            run_git_command(["git", "commit", "-m", commit_message])

            branch_to_push = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            print(f"🚀 Pushing to branch '{branch_to_push}'...")

            if new_branch_created and branch_to_push == branch_name:
                run_git_command(["git", "push", "--set-upstream", "origin", branch_to_push])
            else:
                run_git_command(["git", "push", "origin", branch_to_push])
            
            print("✨ Success!")

            if args.pr:
                pr_url = get_pr_url(branch_to_push)
                if pr_url:
                    open_pr_response = input(f"\n🔗 Would you like to open a Pull Request in your browser? (Y/n): ").strip().lower()
                    if open_pr_response in ('y', ''):
                        print(f"🚀 Opening PR link in your browser...")
                        if not open_in_browser(pr_url):
                            print(f"⚠️ Could not open the browser automatically.")
                            print(f"   Please, copy and paste this URL:\n   {pr_url}")
        else:
            print("🚫 Operation canceled by the user.")
            if new_branch_created and branch_name != original_branch_name:
                go_back = input(f"❓ You created the branch '{branch_name}'. Would you like to return to the original branch '{original_branch_name}'? (y/N): ").strip().lower()
                if go_back == 'y':
                    print(f"↪️ Returning to branch '{original_branch_name}'...")
                    run_git_command(["git", "checkout", original_branch_name])
                    print(f"✅ Returned to '{original_branch_name}'.")
                else:
                    print(f"ℹ️ Staying on branch '{branch_name}'.")
    else:
        print("🚫 Commit canceled.")
        if new_branch_created and branch_name != original_branch_name:
            go_back = input(f"❓ You created the branch '{branch_name}' but canceled the commit. Would you like to return to the original branch '{original_branch_name}'? (y/N): ").strip().lower()
            if go_back == 'y':
                print(f"↪️ Returning to branch '{original_branch_name}'...")
                run_git_command(["git", "checkout", original_branch_name])
                print(f"✅ Returned to '{original_branch_name}'.")
            else:
                print(f"ℹ️ Staying on branch '{branch_name}'.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{MESSAGES['OPERATION_CANCELLED']}")
        exit(130)
