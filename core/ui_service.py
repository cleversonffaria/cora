from utils.constants import *

class UIService:
    def __init__(self):
        pass
    
    def show_version(self):
        print(f"🤖 {COMMAND_NAME.title()} v{VERSION}")
        print("Assistente de fluxo de trabalho Git com IA")
        print(REPOSITORY_URL)

    def show_welcome(self):
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
       {COMMAND_NAME} -b -c -pr       # Fluxo completo: branch + commit + PR

🔑 Não esqueça de configurar sua chave da API no arquivo .env!
""")

    def show_help(self):
        print(f"""🤖 {COMMAND_NAME.title()} v{VERSION} - Assistente de Git com IA

{HELP_SECTIONS["USAGE"]}
  {COMMAND_NAME} [OPÇÕES]

{HELP_SECTIONS["OPTIONS"]}
  -b, --branch         Cria uma nova branch
  -c, --commit         Gera e executa commit
  -pr, --pull-request  {OPTION_DESCRIPTIONS["PR"]}
  -v, --version        {OPTION_DESCRIPTIONS["VERSION"]}
      -h, --help           {OPTION_DESCRIPTIONS["HELP"]}

{HELP_SECTIONS["EXAMPLES"]}
  {COMMAND_NAME} -c                 # Gera apenas commit
  {COMMAND_NAME} -b                 # Cria apenas branch
  {COMMAND_NAME} -b -c              # Cria branch + commit
      {COMMAND_NAME} -c -pr            # Commit + abre PR
    {COMMAND_NAME} -b -c -pr         # Fluxo completo: branch + commit + PR

{HELP_SECTIONS["SETUP"]}
  Configure sua chave da API no arquivo .env:
  {API_KEY_VAR}="sua_chave_aqui"
  {MODEL_VAR}="modelo_desejado"
  {API_BASE_URL_VAR}="url_da_api"

{HELP_SECTIONS["NOTE"]}
  O comando automaticamente adiciona todas as mudanças (git add .) antes de gerar sugestões.
""")
    
    def show_api_key_error(self):
        print(MESSAGES["API_KEY_NOT_SET"])
        print(MESSAGES["API_KEY_HELP"])
    
    def show_no_changes(self):
        print(MESSAGES["NO_CHANGES"])
    
    def show_operation_cancelled(self):
        print(f"\n\n{MESSAGES['OPERATION_CANCELLED']}")
    
    def user_interaction_loop(self, prompt_question, generation_function, diff):
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
    
    def show_commit_review(self, commit_message, current_branch):
        print(f"\n📝 Commit Review:")
        print(f"   Message: \"{commit_message}\"")
        print(f"   Branch: {current_branch}")
    
    def confirm_push(self, current_branch):
        return input(f"\n🚀 Push to remote branch '{current_branch}'? (Y/n): ").strip().lower()
    
    def select_base_branch(self, current_branch, available_branches):
        print(f"📍 Branch atual: {current_branch}")
        print("\n📋 Selecione a branch base para comparação:")
        
        for i, branch in enumerate(available_branches, 1):
            print(f"{i}. {branch}")
        
        try:
            choice = int(input("\n🔢 Digite o número da branch: "))
            if 1 <= choice <= len(available_branches):
                return available_branches[choice - 1]
            else:
                print("❌ Opção inválida.")
                return None
        except ValueError:
            print("❌ Por favor, digite um número válido.")
            return None 