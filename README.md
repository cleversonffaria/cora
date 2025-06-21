# Git AI Assistant
## Features

- ✨ AI-powered suggestions for conventional commit messages.
- 🌿 Smart generation of descriptive branch names.
- 🚀 Full workflow automation: stage, commit, push, and optionally open a pull request.
- 💬 Interactive loop to refine suggestions until they are perfect.

## Prerequisites

- Git
- Python 3.8+

## Installation

This project includes an automated installation script that handles all setup.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/cleversonffaria/cora.git
   cd cora
   ```

2. **Run the installation script:**

   ```bash
   chmod +x install.sh  # Give execution permission
   ./install.sh
   ```

The script will automatically:

- Create a local Python virtual environment (`.venv`).
- Install all the required dependencies into it.
- Create the `cora` command in your system, making it available from any directory.

Follow any instructions provided by the script, such as adding the installation directory to your PATH if it's not already configured.

## Configuration

After running the `install.sh` script, you need to create a `.env` file in the project directory with your API configuration:

### Required Configuration:
```bash
# Your API key (required)
API_KEY="your_api_key_here"
```

### Optional Configuration:
```bash
# Model to use (optional, defaults to gpt-4o-mini)
MODEL="gpt-4o-mini"

# API Base URL (optional, for custom providers)
API_BASE_URL="https://api.provider.com/v1"
```

### Examples for Different Providers:

**OpenAI (default):**
```bash
API_KEY="sk-..."
MODEL="gpt-4o-mini"
API_BASE_URL="https://api.openai.com/v1"  # Optional, this is the default
```

**OpenRouter:**
```bash
API_KEY="sk-or-v1-..."
MODEL="openai/gpt-4o-mini"  # or any model from OpenRouter
API_BASE_URL="https://openrouter.ai/api/v1"
```

**Anthropic Claude (via OpenRouter):**
```bash
API_KEY="sk-or-v1-..."
MODEL="anthropic/claude-3-haiku"
API_BASE_URL="https://openrouter.ai/api/v1"
```

**Other compatible providers:**
```bash
API_KEY="your_key"
MODEL="your_model"
API_BASE_URL="https://your-provider-api-url/v1"
```

## Uninstallation

To completely remove [COMMAND][] from your system:

1. **Give execution permission to the uninstall script:**
   ```bash
   chmod +x uninstall.sh
   ```

2. **Run the uninstall script:**
   ```bash
   ./uninstall.sh
   ```

The uninstall script will:
- Remove the command from your system ($HOME/bin and PowerShell profile)
- Ask if you want to remove the Python virtual environment
- Ask if you want to remove the .env configuration file
- Clean up empty directories
- Create backups of modified files

**Alternative (if you prefer):**
```bash
bash uninstall.sh  # No need for chmod with this method
```

## Usage

The main command is `cora`. You can use flags to customize its behavior.

### Examples

**1. Generate a commit message:**
Simply run the command. It's already add (`git add .`) when you run this command.

```bash
cora
```

2. Generate a branch name, then a commit message:
   Use the --branch (or -b) flag.

```bash
cora --branch
```

3. Full workflow: Branch, Commit, Push, and open PR:
   Combine the --branch and --pr flags for a complete automated workflow.

```bash
cora -b --pr
```

Interactive Prompts

The script will ask for your confirmation at various stages.

    Press Enter or y to accept a suggestion.
    Press r to regenerate a new suggestion.
    Press n to cancel an action.
