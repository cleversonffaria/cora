VERSION = "1.0.0"
COMMAND_NAME = "cora"

REPOSITORY_URL = f"https://github.com/cleversonffaria/{COMMAND_NAME}"

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_BRANCH_TEMPERATURE = 0.5

# API Configuration - these will be overridden by .env values
API_KEY_VAR = "API_KEY"
API_BASE_URL_VAR = "API_BASE_URL"
MODEL_VAR = "MODEL"

MESSAGES = {
    "WELCOME_TITLE": "Bem-vindo ao {command_name} v{version}!",
    "WELCOME_SUBTITLE": "Seu assistente de IA para desenvolvimento Git produtivo",
    "API_KEY_NOT_SET": "❌ API_KEY environment variable not set.",
    "API_KEY_HELP": "   Please define it in your .env file or your environment.",
    "NO_CHANGES": "✅ No staged changes found. Nothing to commit.",
    "OPERATION_CANCELLED": "🚫 Operation canceled by user. Exiting."
}

HELP_SECTIONS = {
    "USAGE": "📋 USO:",
    "OPTIONS": "🔧 OPÇÕES:",
    "EXAMPLES": "✨ EXEMPLOS:",
    "SETUP": "🔑 CONFIGURAÇÃO:",
    "NOTE": "💡 NOTA:"
}

OPTION_DESCRIPTIONS = {
    "BRANCH": "Gera um nome de branch antes de fazer commit",
    "PR": "Abre pull request no navegador após push",
    "VERSION": "Mostra informações da versão",
    "HELP": "Mostra esta mensagem de ajuda"
}

EXAMPLE_DESCRIPTIONS = {
    "COMMIT_ONLY": "Gera apenas mensagem de commit",
    "BRANCH_COMMIT": "Gera branch + mensagem de commit", 
    "FULL_WORKFLOW": "Fluxo completo: branch + commit + push + PR"
}