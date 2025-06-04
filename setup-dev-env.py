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
subprocess.check_call([pip_executable, "install", "-r", "requirements.txt", "-r", "requirements-dev.txt"])

print("Creating hook symlinks")

git_dir = os.path.join(os.getcwd(), ".git")

if not os.path.isdir(git_dir):
    # we are probably a submodule, look for a .git file
    
    if not os.path.isfile(git_dir):
        print("Script could not find .git folder / file.\nPlease make sure to run the script at the repository root.")
    
    with open(git_dir, "r") as f:
        entries = [ entry.split(':', 1) for entry in f.readlines() ]
        config_entries = { entry[0].strip() : entry[1].strip() for entry in entries }

    git_dir = config_entries['gitdir']

pre_push_path = os.path.join(git_dir, "hooks", "pre-push")

with open(pre_push_path, "w") as f:
    f.write("#!/bin/sh\n")
    f.write("env -i ./hooks/pre-push\n")

print("Hooks are now setup!")
