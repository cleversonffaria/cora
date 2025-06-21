# 🤖 Cora - Assistente de Git com IA

> **Automatize seu fluxo de trabalho Git com inteligência artificial**

Cora é um assistente inteligente que utiliza IA para gerar mensagens de commit convencionais, criar nomes de branches descritivos e automatizar completamente seu fluxo de trabalho Git.

## ✨ Funcionalidades

- 🤖 **Mensagens de commit inteligentes**: Gera mensagens seguindo padrões convencionais automaticamente
- 🌿 **Nomes de branches descritivos**: Cria nomes organizados no formato `tipo/descrição`
- 🚀 **Fluxo completo automatizado**: Stage, commit, push e criação de Pull Request
- 💬 **Loop interativo**: Refine sugestões até ficarem perfeitas
- 🔄 **Regeneração inteligente**: Sistema que evita sugestões duplicadas
- 📋 **Pull Requests automáticos**: Criação de PRs com descrições detalhadas geradas por IA
- 🌍 **Multi-provider**: Suporte para OpenAI, OpenRouter, Anthropic e outros provedores compatíveis

## 📋 Pré-requisitos

- **Git** (versão 2.0 ou superior)
- **Python 3.8+**
- **GitHub CLI** (opcional, para criação automática de PRs)
- Chave de API de um provedor de IA compatível

## 🚀 Instalação

### Instalação Automática (Recomendada)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/cleversonffaria/cora.git
   cd cora
   ```

2. **Execute o script de instalação:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

O script irá automaticamente:
- Criar um ambiente virtual Python local (`.venv`)
- Instalar todas as dependências necessárias
- Criar o comando `cora` disponível globalmente
- Configurar o PATH se necessário

### Instalação Manual

Se preferir instalar manualmente:

```bash
# 1. Clone e entre no diretório
git clone https://github.com/cleversonffaria/cora.git
cd cora

# 2. Crie um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Torne o script executável
chmod +x main.py
```

## ⚙️ Configuração

### Configuração Obrigatória

Após a instalação, crie um arquivo `.env` no diretório do projeto:

```bash
# Sua chave de API (obrigatório)
API_KEY="sua_chave_aqui"
# Modelo a ser usado (padrão: openai/gpt-4.1-nano)
MODEL="openai/gpt-4.1-nano"
# URL base da API (para provedores customizados)
API_BASE_URL="https://api.provedor.com/v1"
```

### Exemplos para Diferentes Provedores

**OpenAI (padrão):**
```bash
API_KEY="minha-chave..."
MODEL="gpt-4o-mini"
# API_BASE_URL não é necessário para OpenAI
```

**OpenRouter:**
```bash
API_KEY="minha-chave..."
MODEL="openai/gpt-4.1-nano"
API_BASE_URL="https://openrouter.ai/api/v1"
```

**Anthropic Claude (via OpenRouter):**
```bash
API_KEY="minha-chave..."
MODEL="anthropic/claude-3-haiku"
API_BASE_URL="https://openrouter.ai/api/v1"
```

**Outros provedores compatíveis:**
```bash
API_KEY="sua_chave"
MODEL="seu_modelo"
API_BASE_URL="https://url-do-provedor/v1"
```

## 📖 Como Usar

### Comandos Disponíveis

```bash
cora [OPÇÕES]
```

### Opções

| Opção | Alias | Descrição |
|-------|-------|-----------|
| `--branch` | `-b` | Cria uma nova branch |
| `--commit` | `-c` | Gera e executa commit |
| `--pull-request` | `-pr` | Cria Pull Request |
| `--version` | `-v` | Mostra versão |
| `--help` | `-h` | Mostra ajuda |

### Exemplos de Uso

**1. Apenas commit (modo básico):**
```bash
cora -c
```
*Adiciona todas as mudanças (git add .) e gera um commit inteligente*

**2. Criar branch + commit:**
```bash
cora -b -c
```
*Cria uma nova branch descritiva e faz o commit*

**3. Fluxo completo (branch + commit + PR):**
```bash
cora -b -c -pr
```
*Cria branch, faz commit, push e abre Pull Request*

**4. Apenas criar Pull Request:**
```bash
cora -pr
```
*Cria PR da branch atual para uma branch base selecionada*

**5. Ver informações:**
```bash
cora --version    # Versão do Cora
cora --help       # Ajuda completa
cora              # Tela de boas-vindas
```

### Interação Durante o Uso

Durante a execução, você pode:

- **Enter** ou **Y**: Aceitar a sugestão
- **R**: Regenerar uma nova sugestão (com temperatura maior)
- **N**: Cancelar a operação

## 🔧 Recursos Avançados

### Pull Requests Automáticos

O Cora pode criar PRs automaticamente de duas formas:

1. **Com GitHub CLI** (recomendado):
   - Instale o [GitHub CLI](https://cli.github.com/)
   - Faça login: `gh auth login`
   - O Cora criará PRs automaticamente com descrições detalhadas

2. **Sem GitHub CLI**:
   - Abre automaticamente no navegador a página de criação de PR
   - Descrição gerada por IA é exibida no terminal para copiar

### Geração de Descrições de PR

As descrições de PR incluem:
- **Título** resumido da funcionalidade
- **Descrição** técnica das mudanças
- **Resumo** das principais alterações
- **Contexto** do problema resolvido
- **Solução implementada** com emojis descritivos
- **Impacto esperado** das mudanças

### Sistema de Regeneração Inteligente

- Evita sugestões duplicadas
- Aumenta a "criatividade" (temperature) a cada regeneração
- Mantém histórico das sugestões rejeitadas

## 🛠️ Dependências

### Python (requirements.txt)
```
openai>=1.0.0
python-dotenv>=1.0.0
```

### Sistema
- **Git** (obrigatório)
- **GitHub CLI** (opcional, para PRs automáticos)

## ❌ Desinstalação

Para remover completamente o Cora do sistema:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

O script de desinstalação irá:
- Remover o comando do sistema
- Perguntar se deseja remover o ambiente virtual
- Perguntar se deseja remover o arquivo `.env`
- Limpar diretórios vazios
- Criar backups dos arquivos modificados

## 🐛 Solução de Problemas

### Erros Comuns

**"API key not found"**
```bash
# Verifique se o arquivo .env existe e contém a chave
cat .env
```

**"git command not found"**
```bash
# Instale o Git
# Ubuntu/Debian: sudo apt-get install git
# macOS: brew install git
# Windows: https://git-scm.com/download/win
```

**"No changes detected"**
```bash
# Verifique se há mudanças para commitar
git status
```

**Erro de permissão no comando**
```bash
# Torne o script executável
chmod +x main.py
```

### GitHub CLI (Opcional)

Para PRs automáticos, instale e configure:

```bash
# Instalar GitHub CLI
# macOS:
brew install gh

# Ubuntu/Debian:
sudo apt-get install gh

# Windows:
winget install GitHub.cli

# Configurar
gh auth login
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔗 Links Úteis

- **Repositório**: [https://github.com/cleversonffaria/cora](https://github.com/cleversonffaria/cora)
- **Issues**: [https://github.com/cleversonffaria/cora/issues](https://github.com/cleversonffaria/cora/issues)
- **Conventional Commits**: [https://www.conventionalcommits.org/](https://www.conventionalcommits.org/)
- **GitHub CLI**: [https://cli.github.com/](https://cli.github.com/)

## ⭐ Se Gostou do Projeto

Se o Cora foi útil para você, considere dar uma ⭐ no repositório!

---

**Desenvolvido com ❤️ por [Cleverson Fernandes](https://github.com/cleversonffaria)**
**Colaboração: [Yuri Costa](https://github.com/YuriRCosta)**
