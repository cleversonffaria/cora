#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/bin"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

if [ -f "$PROJECT_DIR/utils/constants.py" ]; then
  COMMAND_NAME=$(python3 -c "import sys; sys.path.append('$PROJECT_DIR'); from utils.constants import COMMAND_NAME; print(COMMAND_NAME)")
else
  echo -e "${YELLOW}WARNING: utils/constants.py not found. Using default command name 'cora'.${NC}"
  COMMAND_NAME="cora"
fi

echo -e "${GREEN}Starting the installation of ${COMMAND_NAME}...${NC}"

if ! command -v python3 &>/dev/null; then
  echo -e "${YELLOW}ERROR: python3 is not installed. Please install it to continue.${NC}"
  exit 1
fi

echo -e "\nCreating Python virtual environment in '$VENV_DIR'..."
python3 -m venv "$VENV_DIR"

echo "Activating virtual environment to install dependencies..."
source "$VENV_DIR/bin/activate"

if [ -f "requirements.txt" ]; then
  echo "Installing Python dependencies from requirements.txt..."
  pip install -r requirements.txt
else
  echo -e "${YELLOW}WARNING: requirements.txt not found. Skipping dependency installation.${NC}"
fi

deactivate
echo "Virtual environment setup complete."

mkdir -p "$INSTALL_DIR"

echo "Creating wrapper script at '$INSTALL_DIR/$COMMAND_NAME'..."
WRAPPER_SCRIPT_PATH="$INSTALL_DIR/$COMMAND_NAME"

cat >"$WRAPPER_SCRIPT_PATH" <<EOF
#!/bin/bash
# Wrapper to run $COMMAND_NAME using its virtual environment
exec "$VENV_DIR/bin/python" "$PROJECT_DIR/main.py" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT_PATH"

# Setup PowerShell profile if PowerShell is available
if command -v pwsh &>/dev/null; then
  echo -e "\n${BLUE}PowerShell detected! Setting up PowerShell profile...${NC}"
  
  # Get PowerShell profile path
  POWERSHELL_PROFILE=$(pwsh -NoProfile -Command 'Write-Output $PROFILE' 2>/dev/null || echo "")
  
  if [ -n "$POWERSHELL_PROFILE" ]; then
    # Create profile directory if it doesn't exist
    PROFILE_DIR=$(dirname "$POWERSHELL_PROFILE")
    mkdir -p "$PROFILE_DIR"
    
    # Create profile file if it doesn't exist
    if [ ! -f "$POWERSHELL_PROFILE" ]; then
      touch "$POWERSHELL_PROFILE"
      echo "# PowerShell Profile" > "$POWERSHELL_PROFILE"
    fi
    
    # Check if function already exists
    if ! grep -q "function $COMMAND_NAME" "$POWERSHELL_PROFILE" 2>/dev/null; then
      echo -e "\n# Auto-generated function for $COMMAND_NAME" >> "$POWERSHELL_PROFILE"
      echo "function $COMMAND_NAME { & \"$VENV_DIR/bin/python\" \"$PROJECT_DIR/main.py\" \$args }" >> "$POWERSHELL_PROFILE"
      echo -e "${GREEN}✅ PowerShell function '$COMMAND_NAME' added to profile!${NC}"
      echo -e "   Profile: $POWERSHELL_PROFILE"
    else
      echo -e "${YELLOW}⚠️  PowerShell function '$COMMAND_NAME' already exists in profile.${NC}"
    fi
  else
    echo -e "${YELLOW}⚠️  Could not detect PowerShell profile path.${NC}"
  fi
else
  echo -e "\n${YELLOW}PowerShell not detected. Skipping PowerShell setup...${NC}"
fi

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
  echo -e "\n${YELLOW}WARNING: Your directory '$INSTALL_DIR' is not in your PATH.${NC}"
  echo "Please add '$INSTALL_DIR' to your PATH to use the '${COMMAND_NAME}' command."
  echo "You can do this by adding the following line to your shell config (e.g., ~/.bashrc, ~/.zshrc):"
  echo -e "\n  ${GREEN}export PATH=\"$INSTALL_DIR:\$PATH\"${NC}\n"
  echo "Then, restart your terminal."
fi

if [ ! -f .env ]; then
  echo -e "\nCreating configuration file '.env'..."
  cat > .env << 'EOF'
# API Configuration
# Your API key (required)
API_KEY="your_api_key_here"

# Model to use (optional, defaults to openai/gpt-4.1-nano)
MODEL="openai/gpt-4.1-nano"

# API Base URL (optional, defaults to OpenAI)
API_BASE_URL="https://api.openai.com/v1"

# Examples for different providers:
#
# OpenAI (default):
# API_KEY="sk-..."
# MODEL="openai/gpt-4.1-nano"
# API_BASE_URL="https://api.openai.com/v1"
#
# OpenRouter:
# API_KEY="sk-or-v1-..."
# MODEL="openai/openai/gpt-4.1-nano"
# API_BASE_URL="https://openrouter.ai/api/v1"
EOF
  echo -e "${YELLOW}ACTION REQUIRED: Edit the '.env' file and configure your API settings.${NC}"
else
  echo -e "\n'.env' file already exists. No changes were made."
fi

echo -e "\n${GREEN}Installation completed successfully!${NC}"
echo "Please restart your terminal or source your shell config file for the '${COMMAND_NAME}' command to be recognized."
