#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/bin"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

# Get COMMAND_NAME from utils/constants.py
if [ -f "$PROJECT_DIR/utils/constants.py" ]; then
  COMMAND_NAME=$(python3 -c "import sys; sys.path.append('$PROJECT_DIR'); from utils.constants import COMMAND_NAME; print(COMMAND_NAME)")
else
  echo -e "${YELLOW}WARNING: utils/constants.py not found. Using default command name 'cora'.${NC}"
  COMMAND_NAME="cora"
fi

echo -e "${RED}🗑️  Starting uninstallation of ${COMMAND_NAME}...${NC}"

# Remove wrapper script from install directory
WRAPPER_SCRIPT_PATH="$INSTALL_DIR/$COMMAND_NAME"
if [ -f "$WRAPPER_SCRIPT_PATH" ]; then
  echo -e "\n${BLUE}Removing wrapper script: $WRAPPER_SCRIPT_PATH${NC}"
  rm -f "$WRAPPER_SCRIPT_PATH"
  echo -e "${GREEN}✅ Wrapper script removed.${NC}"
else
  echo -e "${YELLOW}⚠️  Wrapper script not found: $WRAPPER_SCRIPT_PATH${NC}"
fi

# Remove PowerShell function if PowerShell is available
if command -v pwsh &>/dev/null; then
  echo -e "\n${BLUE}Checking PowerShell profile...${NC}"
  
  POWERSHELL_PROFILE=$(pwsh -NoProfile -Command 'Write-Output $PROFILE' 2>/dev/null || echo "")
  
  if [ -n "$POWERSHELL_PROFILE" ] && [ -f "$POWERSHELL_PROFILE" ]; then
    if grep -q "function $COMMAND_NAME" "$POWERSHELL_PROFILE" 2>/dev/null; then
      echo -e "${BLUE}Removing PowerShell function from profile...${NC}"
      
      # Create backup
      cp "$POWERSHELL_PROFILE" "$POWERSHELL_PROFILE.backup"
      
      # Remove the function and comment lines
      sed -i.tmp "/# Auto-generated function for $COMMAND_NAME/d" "$POWERSHELL_PROFILE"
      sed -i.tmp "/function $COMMAND_NAME { /d" "$POWERSHELL_PROFILE"
      
      # Clean up temp file
      rm -f "$POWERSHELL_PROFILE.tmp"
      
      echo -e "${GREEN}✅ PowerShell function removed.${NC}"
      echo -e "${BLUE}   Backup created: $POWERSHELL_PROFILE.backup${NC}"
    else
      echo -e "${YELLOW}⚠️  PowerShell function not found in profile.${NC}"
    fi
  else
    echo -e "${YELLOW}⚠️  PowerShell profile not found or empty.${NC}"
  fi
else
  echo -e "\n${YELLOW}PowerShell not detected. Skipping PowerShell cleanup...${NC}"
fi

# Ask about virtual environment
echo -e "\n${YELLOW}🤔 Do you want to remove the Python virtual environment?${NC}"
echo -e "   This will delete: $VENV_DIR"
read -p "   Remove virtual environment? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Removing virtual environment...${NC}"
    rm -rf "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment removed.${NC}"
  else
    echo -e "${YELLOW}⚠️  Virtual environment not found: $VENV_DIR${NC}"
  fi
else
  echo -e "${BLUE}ℹ️  Virtual environment kept.${NC}"
fi

# Ask about .env file
echo -e "\n${YELLOW}🤔 Do you want to remove the .env configuration file?${NC}"
echo -e "   This contains your API key and other settings."
read -p "   Remove .env file? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  if [ -f "$PROJECT_DIR/.env" ]; then
    echo -e "${BLUE}Removing .env file...${NC}"
    rm -f "$PROJECT_DIR/.env"
    echo -e "${GREEN}✅ .env file removed.${NC}"
  else
    echo -e "${YELLOW}⚠️  .env file not found.${NC}"
  fi
else
  echo -e "${BLUE}ℹ️  .env file kept.${NC}"
fi

# Final cleanup check
echo -e "\n${BLUE}🧹 Final cleanup...${NC}"

# Check if install directory is empty and remove it
if [ -d "$INSTALL_DIR" ]; then
  if [ -z "$(ls -A $INSTALL_DIR)" ]; then
    echo -e "${BLUE}Removing empty $INSTALL_DIR directory...${NC}"
    rmdir "$INSTALL_DIR"
    echo -e "${GREEN}✅ Empty $INSTALL_DIR directory removed.${NC}"
  else
    echo -e "${BLUE}ℹ️  $INSTALL_DIR directory contains other files, keeping it.${NC}"
  fi
fi

echo -e "\n${GREEN}🎉 Uninstallation completed!${NC}"
echo -e "\n${BLUE}📋 Summary:${NC}"
echo -e "• Command '$COMMAND_NAME' removed from system"
echo -e "• PowerShell function cleaned up"
echo -e "• Virtual environment: $([ -d "$VENV_DIR" ] && echo "kept" || echo "removed")"
echo -e "• Configuration file: $([ -f "$PROJECT_DIR/.env" ] && echo "kept" || echo "removed")"

echo -e "\n${YELLOW}💡 Note: You may need to restart your terminal for changes to take effect.${NC}" 