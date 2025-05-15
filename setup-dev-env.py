import venv
import os
import subprocess

venv_bin_folder = 'Scripts' if os.name == 'nt' else 'bin'

print("Creating virtual environment")

venv_dir = os.path.join(os.getcwd(), ".venv")
builder = venv.EnvBuilder(with_pip=True)
builder.create(venv_dir)

print("Installing venv dependencies")

pip_executable = os.path.join(venv_dir, venv_bin_folder, "pip.exe")
subprocess.check_call([pip_executable, "install", "-r", "requirements.txt"])

print("Creating hook symlinks")

hooks_dir = os.path.join(os.getcwd(), ".git", "hooks")
pre_push_path = os.path.join(hooks_dir, "pre-push")

with open(pre_push_path, "w") as f:
    f.write("#!/bin/sh\n")
    f.write("env -i ./hooks/pre-push\n")

print("Hooks are now setup!")
