import subprocess
import sys

def install(module_name: str):
    command = [sys.executable, "-m", "pip", "install", module_name]

    subprocess.run(command)