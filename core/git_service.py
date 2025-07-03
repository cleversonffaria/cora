import subprocess

class GitService:
    def __init__(self):
        pass
    
    def run_command(self, command, check=True):
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=check,
                encoding='utf-8'
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing: {' '.join(command)}")
            print(f"  {e.stderr.strip()}")
            exit(1)
        except FileNotFoundError:
            print(f"❌ git command not found. Please ensure Git is installed and in your PATH.")
            exit(1)
    
    def get_diff(self):
        self.run_command(["git", "add", "."])
        diff = self.run_command(["git", "diff", "--cached"])
        return diff
    
    def get_current_branch(self):
        try:
            return self.run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        except:
            return None
    
    def get_local_branches(self):
        try:
            branches_output = self.run_command(["git", "branch", "--list"])
            branches = []
            for line in branches_output.split('\n'):
                branch = line.strip().replace('*', '').strip()
                if branch and (
                    '/' not in branch or
                    branch.startswith('feat/rebrand') or
                    branch.startswith('feat/marketplace')
                ):
                    branches.append(branch)
            return branches
        except:
            return []
    
    def get_branch_diff(self, base_branch, current_branch):
        try:
            diff = self.run_command(["git", "diff", f"{base_branch}..{current_branch}"])
            return diff
        except:
            return None
    
    def create_branch(self, branch_name):
        try:
            self.run_command(["git", "checkout", "-b", branch_name], check=False)
            current_branch_check = self.run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            return current_branch_check == branch_name
        except:
            return False
    
    def commit(self, message):
        try:
            self.run_command(["git", "commit", "-m", message])
            return True
        except:
            return False
    
    def push(self, branch_name, set_upstream=False):
        try:
            if set_upstream:
                self.run_command(["git", "push", "--set-upstream", "origin", branch_name])
            else:
                self.run_command(["git", "push", "origin", branch_name])
            return True
        except:
            return False
    
    def get_remote_url(self):
        try:
            return self.run_command(["git", "config", "--get", "remote.origin.url"])
        except:
            return None
    
    def get_pr_url(self, branch_name):
        try:
            remote_url = self.get_remote_url()
            if not remote_url:
                return None

            if remote_url.startswith("https://"):
                repo_path = remote_url.replace("https://github.com/", "").replace(".git", "")
            elif remote_url.startswith("git@"):
                repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
            else:
                return None

            return f"https://github.com/{repo_path}/pull/new/{branch_name}"
        except Exception:
            return None 