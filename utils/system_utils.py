import subprocess
import sys

class SystemUtils:
    def __init__(self):
        pass
    
    def open_in_browser(self, url):
        command = []
        if sys.platform.startswith('linux'):
            command = ['xdg-open', url]
        elif sys.platform == 'darwin':
            command = ['open', url]
        elif sys.platform == 'win32':
            command = ['start', url]
        
        if not command:
            return False

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False 