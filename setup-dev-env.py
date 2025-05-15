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

src = os.path.join(os.getcwd(), "hooks", "pre-push")
dst = os.path.join(os.getcwd(), ".git", "hooks", "pre-push")

if os.path.exists(dst):
    os.remove(dst)

os.symlink(src, dst)

print("Hooks are now setup!")
