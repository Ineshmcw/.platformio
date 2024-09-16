
import os
import shutil
import subprocess
import sys
import tempfile
from base64 import b64decode

def check_pip_installed():
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], check=True)
        print("pip is already installed.")
        return True
    except subprocess.CalledProcessError:
        print("pip is not installed.")
        return False

def install_pip():
    try:
        subprocess.run([sys.executable, '-m', 'ensurepip'], check=True)
        print("pip has been installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install pip: {e}")
        sys.exit(1)

def bootstrap():
    try:
        subprocess.call(
            [
                "git",
                "clone",
                "https://github.com/MohammedTaherMcW/Innatera_core_installer.git",
            ]
        )
    except subprocess.CalledProcessError as exc:
        print("File exist")  
        
    import pioinstaller.__main__

    pioinstaller.__main__.main()
    os.remove("/Innatera_core_installer")

def main():        
        sys.path.insert(0, os.getcwd()+"/Innatera_core_installer")        
        bootstrap()

if __name__ == "__main__":
    main()
