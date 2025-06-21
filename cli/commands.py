import argparse
from core.ai_service import AIService
from core.git_service import GitService
from core.github_service import GitHubService
from core.ui_service import UIService
from utils.constants import OPTION_DESCRIPTIONS

class CoraCommands:
    def __init__(self):
        self.ai_service = AIService()
        self.git_service = GitService()
        self.github_service = GitHubService()
        self.ui_service = UIService()
    
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Assistente de fluxo de trabalho Git com IA", add_help=False)
        parser.add_argument("--branch", "-b", action="store_true", help="Cria uma nova branch")
        parser.add_argument("--commit", "-c", action="store_true", help="Gera e executa commit")
        parser.add_argument("--pull-request", "-pr", action="store_true", help=OPTION_DESCRIPTIONS["PR"])
        parser.add_argument("--version", "-v", "--v", "-version", action="store_true", help=OPTION_DESCRIPTIONS["VERSION"])
        parser.add_argument("--help", "-h", action="store_true", help=OPTION_DESCRIPTIONS["HELP"])
        return parser.parse_args()
    
    def handle_branch_creation(self, diff):
        print("🌿 Creating new branch...")
        branch_name = self.ui_service.user_interaction_loop(
            "Suggested branch name", 
            self.ai_service.generate_branch_name, 
            diff
        )
        
        if not branch_name:
            print("🚫 Branch creation canceled.")
            return None, False
        
        original_branch = self.git_service.get_current_branch()
        if branch_name == original_branch:
            print(f"⚠️ The suggested branch ('{branch_name}') is the same as the current branch. No new branch will be created.")
            return branch_name, False
        
        print(f"🌿 Creating and checking out branch '{branch_name}'...")
        if self.git_service.create_branch(branch_name):
            print(f"✅ Switched to new branch '{branch_name}'.")
            return branch_name, True
        else:
            print(f"⚠️ Could not create or switch to branch '{branch_name}'. Check if it already exists or if there are conflicts.")
            print(f"   Continuing on branch '{original_branch}'.")
            return None, False
    
    def handle_commit_creation(self, diff, new_branch_created=False):
        print("📝 Creating commit...")
        commit_message = self.ui_service.user_interaction_loop(
            "Suggested commit message", 
            self.ai_service.generate_commit_message, 
            diff
        )
        
        if not commit_message:
            print("🚫 Commit canceled.")
            return False
        
        current_branch = self.git_service.get_current_branch()
        self.ui_service.show_commit_review(commit_message, current_branch)
        
        print("\n💾 Creating commit...")
        if not self.git_service.commit(commit_message):
            print("❌ Failed to create commit.")
            return False
        
        print("✅ Commit created successfully!")
        
        push_confirmation = self.ui_service.confirm_push(current_branch)
        
        if push_confirmation in ('y', ''):
            print(f"🚀 Pushing to branch '{current_branch}'...")
            if self.git_service.push(current_branch, set_upstream=new_branch_created):
                print("✨ Push successful!")
            else:
                print("❌ Push failed.")
                return False
        else:
            print("ℹ️ Commit created locally. Push skipped.")
            print(f"   To push later, run: git push origin {current_branch}")
        
        return True
    
    def handle_pull_request_creation(self):
        print("📋 Iniciando processo de criação de Pull Request...")
        
        current_branch = self.git_service.get_current_branch()
        if not current_branch:
            print("❌ Não foi possível obter a branch atual.")
            return
        
        branches = self.git_service.get_local_branches()
        if not branches:
            print("❌ Nenhuma branch disponível para comparação.")
            return
        
        available_branches = [b for b in branches if b != current_branch]
        if not available_branches:
            print("❌ Nenhuma branch base disponível para comparação.")
            return
        
        base_branch = self.ui_service.select_base_branch(current_branch, available_branches)
        if not base_branch:
            return
        
        print(f"✅ Comparando {current_branch} com {base_branch}")
        
        description = None
        if self.ai_service.is_configured():
            diff = self.git_service.get_branch_diff(base_branch, current_branch)
            if diff:
                description = self.ai_service.generate_pr_description(diff)
            else:
                print("⚠️ Nenhuma diferença encontrada entre as branches.")
                return
        
        if not description:
            description = f"PR automático: {current_branch} to {base_branch}"
        
        self.github_service.display_pr_description(base_branch, current_branch, description)
        
        github_cli_available = self.github_service.check_cli_available()
        pr_created_successfully = False
        
        if github_cli_available:
            print("✅ GitHub CLI autenticado. Tentando criar PR automaticamente...")
            pr_url = self.github_service.create_pr_with_cli(base_branch, current_branch, description)
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
        
        if not pr_created_successfully:
            self.github_service.open_pr_in_browser(current_branch)
    
    def execute(self):
        args = self.parse_arguments()
        
        if args.help:
            self.ui_service.show_help()
            return
        
        if args.version:
            self.ui_service.show_version()
            return
        
        if not any([args.branch, args.commit, args.pull_request]):
            self.ui_service.show_welcome()
            return
        
        if args.branch or args.commit:
            if not self.ai_service.is_configured():
                self.ui_service.show_api_key_error()
                exit(1)
            
            diff = self.git_service.get_diff()
            if not diff:
                self.ui_service.show_no_changes()
                exit(0)
        
        original_branch_name = self.git_service.get_current_branch()
        branch_name = None
        new_branch_created = False
        
        if args.branch:
            branch_name, new_branch_created = self.handle_branch_creation(diff)
            if branch_name is None and not new_branch_created:
                return
        
        if args.commit:
            if not self.handle_commit_creation(diff, new_branch_created):
                return
        
        if args.pull_request:
            self.handle_pull_request_creation() 