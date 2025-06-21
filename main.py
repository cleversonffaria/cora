#!/usr/bin/env python3

from cli.commands import CoraCommands
from core.ui_service import UIService

def main():
    ui_service = UIService()
    cora_commands = CoraCommands()
    
    try:
        cora_commands.execute()
    except KeyboardInterrupt:
        ui_service.show_operation_cancelled()
        exit(130)

if __name__ == "__main__":
    main()
