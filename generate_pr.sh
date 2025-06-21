#!/bin/bash

# Carrega variáveis do .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "Arquivo .env não encontrado em: $ENV_FILE"
  exit 1
fi

# Verifica se BOT_PATH foi definido
if [ -z "$BOT_PATH" ]; then
  echo "Erro: BOT_PATH não está definido no arquivo .env"
  echo "Adicione a linha: BOT_PATH=\"$SCRIPT_DIR\" no seu arquivo .env"
  exit 1
fi

# Checa se está em um repositório Git
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Você precisa rodar esse script dentro de um repositório Git válido."
  exit 1
fi

# Lista branches locais que NÃO contêm '/' no nome
branches=($(git branch --list | sed 's/^[* ] //' | grep -v '/' | tr -d ' '))

if [ ${#branches[@]} -eq 0 ]; then
  echo "Nenhuma branch base encontrada."
  exit 1
fi

echo "Escolha a branch base para comparação:"
for i in "${!branches[@]}"; do
  echo "$((i + 1)). ${branches[$i]}"
done

read -p "Digite o número da branch: " idx

if ! [[ "$idx" =~ ^[0-9]+$ ]] || [ "$idx" -lt 1 ] || [ "$idx" -gt "${#branches[@]}" ]; then
  echo "Opção inválida."
  exit 1
fi

base_branch="${branches[$((idx - 1))]}"
current_branch=$(git rev-parse --abbrev-ref HEAD)

echo "Comparando a branch atual '$current_branch' com '$base_branch'..."

# Gere o diff no diretório do bot
git diff "$base_branch..$current_branch" >"$BOT_PATH/pr_report.txt"
echo "Diff salvo em pr_report.txt"

# Chama o Python para gerar a descrição
python3 "$BOT_PATH/bot_pr.py"

# Verifica se o usuário está autenticado no GitHub CLI
if gh auth status >/dev/null 2>&1; then
  echo "Usuário autenticado no GitHub CLI."

  # Verifica se consegue acessar o repositório remoto
  if gh repo view >/dev/null 2>&1; then
    echo "Repositório acessível. Criando PR automaticamente..."
    echo "Descrição gerada em pr_description.txt"

    # Abre o Pull Request automaticamente
    if gh pr create --base "$base_branch" --title "PR automático: $current_branch -> $base_branch" --body-file "$BOT_PATH/pr_description.txt"; then
      echo "PR criado com sucesso!"
    else
      echo "Erro ao criar PR. Exibindo descrição no terminal:"
      echo "=========================================="
      echo "TÍTULO: PR automático: $current_branch -> $base_branch"
      echo "BASE: $base_branch"
      echo "HEAD: $current_branch"
      echo "=========================================="
      echo "DESCRIÇÃO:"
      cat "$BOT_PATH/pr_description.txt"
      echo "=========================================="
    fi

    # Limpa o arquivo temporário
    rm "$BOT_PATH/pr_report.txt"
  else
    echo "Não foi possível acessar o repositório remoto. Exibindo descrição do PR no terminal:"
    echo "=========================================="
    echo "TÍTULO: PR automático: $current_branch -> $base_branch"
    echo "BASE: $base_branch"
    echo "HEAD: $current_branch"
    echo "=========================================="
    echo "DESCRIÇÃO:"
    cat "$BOT_PATH/pr_description.txt"
    echo ""
    echo ""
    echo "=========================================="
    echo ""
    echo "Verifique se:"
    echo "1. O repositório remoto está configurado: git remote -v"
    echo "2. Você tem acesso ao repositório no GitHub"
    echo "3. O nome do repositório está correto"

    # Limpa os arquivos temporários
    rm "$BOT_PATH/pr_report.txt"
    rm "$BOT_PATH/pr_description.txt"
  fi
else
  echo "GitHub CLI não está autenticado. Exibindo descrição do PR no terminal:"
  echo "=========================================="
  echo "TÍTULO: PR automático: $current_branch -> $base_branch"
  echo "BASE: $base_branch"
  echo "HEAD: $current_branch"
  echo "=========================================="
  echo "DESCRIÇÃO:"
  cat "$BOT_PATH/pr_description.txt"
  echo "=========================================="
  echo ""
  echo "Para autenticar no GitHub CLI, execute: gh auth login"
  echo "Após autenticar, execute novamente este script para criar o PR automaticamente."

  # Limpa os arquivos temporários
  rm "$BOT_PATH/pr_report.txt"
  rm "$BOT_PATH/pr_description.txt"
fi
