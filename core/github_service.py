import subprocess
import tempfile
import os
from core.git_service import GitService
from utils.system_utils import SystemUtils

class GitHubService:
    def __init__(self):
        self.git_service = GitService()
        self.system_utils = SystemUtils()
    
    def check_cli_available(self):
        try:
            self.git_service.run_command(["gh", "--version"])
            self.git_service.run_command(["gh", "auth", "status"])
            self.git_service.run_command(["gh", "repo", "view"])
            return True
        except:
            return False
    
    def create_pr_with_cli(self, base_branch, current_branch, description):
        try:
            title = f"PR: {current_branch} to {base_branch}"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(description)
                temp_file_path = temp_file.name
            
            pr_url = self.git_service.run_command([
                "gh", "pr", "create", 
                "--base", base_branch,
                "--title", title,
                "--body-file", temp_file_path
            ])
            
            os.unlink(temp_file_path)
            
            return pr_url.strip()
        except Exception as e:
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass
                
            error_msg = str(e)
            if "must be a collaborator" in error_msg:
                print("⚠️ Você não tem permissão de colaborador neste repositório.")
                print("   Continuando com método alternativo...")
            elif "uncommitted changes" in error_msg:
                print("⚠️ Há alterações não commitadas.")
                print("   Faça commit das alterações antes de criar o PR.")
            else:
                print(f"❌ Erro ao criar PR: {e}")
            return None
    
    def open_pr_in_browser(self, branch_name):
        pr_url = self.git_service.get_pr_url(branch_name)
        if pr_url:
            print("🚀 Abrindo PR no navegador...")
            if not self.system_utils.open_in_browser(pr_url):
                print(f"⚠️ Não foi possível abrir o navegador automaticamente.")
                print(f"   Copie e cole esta URL:\n   {pr_url}")
                return False
            else:
                print("✅ PR aberto no navegador!")
                return True
        else:
            print("⚠️ Não foi possível gerar URL do PR. Verifique se há um remote GitHub válido.")
            return False
    
    def display_pr_description(self, base_branch, current_branch, description):
        if description:
            print("\n\n" + "="*70)
            print("📋 DESCRIÇÃO DO PULL REQUEST")
            print("="*70)
            print(f"TÍTULO: PR: {current_branch} to {base_branch}")
            print(f"BASE: {base_branch}")
            print(f"HEAD: {current_branch}")
            print("="*70)
            print("DESCRIÇÃO:")
            print()
            print(description)
            print()
            print("="*70 + "\n\n") 