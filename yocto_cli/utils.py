import hashlib
import json
import logging
import os
import subprocess as sp
import sys
import shlex

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def err(msg):
    logging.error(msg)
    sys.exit()


def dbg(msg):
    logging.info(msg)


def execute(cmd, cwd=None):
    try:
        result = sp.run(
            cmd, check=True, stderr=sp.STDOUT, cwd=cwd, text=True
        )
        if result.stdout:
            dbg(result.stdout)
    except sp.CalledProcessError as e:
        err(f"Error running {cmd}: {e.output}")
    except Exception as e:
        err(str(e))


def check_output(cmd, cwd=None):
    try:
        output = sp.check_output(cmd, text=True, cwd=cwd)
        return output.strip()
    except sp.CalledProcessError as e:
        dbg(e)
        return ""


def clone_repo(url, branch, cwd):
    if not url:
        return

    repo_name = url.split("/")[-1].replace(".git", "")
    if os.path.exists(os.path.join(cwd, repo_name)):
        dbg(f"Repo {repo_name} already exists. Skipping...")
        return

    for attempt in range(3):  # Retry up to 3 times
        try:
            dbg(f"Cloning {url} (Attempt {attempt+1}/3)...")
            cmd = f"git clone {url} -b {branch}"
            execute(shlex.split(cmd), cwd=cwd)
            return
        except:
            dbg(f"Attempt {attempt+1} failed for {url}")

    err(f"Unable to clone {url} after 3 attempts. Try cloning manually.")


def sha256sum(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_config(config_path):
    with open(config_path) as f:
        config = json.load(f)
    return config


def parse_config(config, build_type):
    localconf = "\n\n"
    bblayers = "\n\n"
    machine = config.get("machine")
    if not machine:
        machine = config["default_machines"][build_type]

    localconf += f'MACHINE="{machine}"\n'
    localconf += "\n".join(config["other_conf"]) + "\n"

    layers = config["layers"]["base"]
    if build_type and build_type != "base":
        layers += config["layers"][build_type]

    _bblayers = []
    for layer in layers:
        _bblayers += layer["bblayers"]

    for bblayer in _bblayers:
        bblayers += f'BBLAYERS += "../sources/{bblayer}"'

    return (localconf, bblayers)


def update_file_content(filepath, marker, new_section):
    if not os.path.exists(filepath):
        err("Configs not found. Run source sources/poky/oe-init-build-env")

    with open(filepath, "r") as f:
        lines = f.readlines()

    output = []
    in_marker = False
    marker_found = False

    for line in lines:
        if f"# {marker}" in line:
            marker_found = True
            output.append(line)
            in_marker = True
            continue
        if in_marker:
            continue
        output.append(line)

    if not marker_found:
        output.append(f"# {marker}\n")

    output.append(new_section + "\n")

    with open(filepath, "w") as f:
        f.writelines(output)
    dbg(f"Updated {filepath} under marker: #{marker}")
