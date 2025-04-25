import argparse
import os
import time
from pathlib import Path

from yocto_cli import docker
from yocto_cli import utils
from yocto_cli.utils import dbg, err


class YoctoCLI:
    def __init__(self, **kwargs) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-b",
            "--branch",
            help="Specify Yocto branch to use for the build",
            default="master",
            dest="branch",
        )
        parser.add_argument(
            "-w",
            "--workspace",
            help="Specify the path to setup the build",
            default=os.path.join(Path.home(), "workspace", "yocto"),
            dest="workspace",
        )
        parser.add_argument(
            "-d",
            "--docker-file",
            help="Specify the path to Dockerfile",
            default=os.path.join(Path(__file__).parent.resolve(), "artifacts", "Dockerfile"),
            dest="dockerfile_path",
        )
        parser.add_argument(
            "-c",
            "--config-file",
            help="Specify the path to config.json file to configure the yocto build",
            default=os.path.join(Path(__file__).parent.resolve(), "artifacts", "config.json"),
            dest="config_path",
        )
        parser.add_argument(
            "-x",
            "--run-cmd",
            help="Run command inside bitbake environment. \
                Helpful for cases when you need to run commands like \
                bitbake -c cleanall <target>",
            dest="run_cmd",
        )

        parser.add_argument(
            "--build-container",
            help="Rebuild the docker container",
            action="store_true",
            dest="build_container",
        )
        parser.add_argument(
            "--build-type",
            choices=["base", "tegra", "freescale"],
            help="Specify the BSP build type",
            default="base",
            dest="build_type",
        )
        parser.add_argument(
            "--setup_only",
            help="Only run setup and configuration. Will not initiate the yocto build",
            action="store_true",
            dest="setup_only",
        )

        args = parser.parse_args()
        for key, val in args.__dict__.items():
            setattr(self, key, val)

        self.config = utils.load_config(self.config_path)
        self.target = self.config["target"]
        self.container_name = f"docker_{self.branch}"
        self.image_name = "ycinst:latest"

    def setup(self):
        # Initiate setup location
        src_dir = os.path.join(os.path.abspath(self.workspace), self.branch, "sources")
        os.makedirs(src_dir, exist_ok=True)
        dbg(f"Source dir: {src_dir}")

        # Download Repos
        layers = self.config["layers"]["base"]
        if self.build_type and self.build_type != "base":
            layers += self.config["layers"][self.build_type]
        for layer in layers:
            utils.clone_repo(layer.get("url", ""), self.branch, src_dir)

        # Check if container is already running
        container_running = docker.get_container(self.container_name)

        if self.build_container and container_running:
            dbg(
                f"Docker container {self.container_name} is already running. Restarting..."
            )
            utils.execute(["docker", "stop", self.container_name])

        # Build Docker image if not present or --build-container passed
        have_image = docker.get_image(self.image_name)
        if not have_image or self.build_container:
            base_dir = os.path.dirname(self.dockerfile_path)
            docker.build_image(self.image_name, self.dockerfile_path, base_dir)

        # Start container if not running
        workspace_host = os.path.join(os.path.abspath(self.workspace), self.branch)
        workspace_container = "/home/yocto"

        if not container_running or self.build_container:
            dbg(f"Launching container {self.container_name}...")
            docker.run_container(self.container_name, workspace_host, workspace_container)

        # Initialize build env if configs doesn't exist
        build_conf_dir = os.path.join(workspace_host, "build", "conf")
        local_conf = os.path.join(build_conf_dir, "local.conf")

        if not os.path.exists(local_conf):
            dbg("Initializing build environment inside container...")
            docker.exec_cmd("source /home/yocto/sources/poky/oe-init-build-env", self.container_name, with_bb_env=False)

        dbg("Setup completed !!!")

    def configure(self):
        workspace_host = os.path.join(os.path.abspath(self.workspace), self.branch)
        build_conf_dir = os.path.join(workspace_host, "build", "conf")

        # Look for the changes in the config
        previous_hash = os.path.join(build_conf_dir, "conf.hash")
        calculated_hash = utils.sha256sum(self.config_path)

        if os.path.exists(previous_hash):
            with open(previous_hash, "r") as f:
                saved_hash = f.read().strip()
            if calculated_hash == saved_hash:
                dbg("Configuration already up to date.")
                return

        dbg("Changes detected in config")
        local_conf_content, bblayer_content = utils.parse_config(self.config, self.build_type)

        # Update local.conf
        dbg("Updating local.conf")
        local_conf = os.path.join(build_conf_dir, "local.conf")
        utils.update_file_content(local_conf, "User-Config", local_conf_content)

        # Update bblayers.conf
        dbg("Updating bblayers.conf")
        bblayers_conf = os.path.join(build_conf_dir, "bblayers.conf")
        utils.update_file_content(bblayers_conf, "User-Layers", bblayer_content)

        with open(previous_hash, "w") as f:
            f.write(calculated_hash)

        dbg("Configuration completed !!!")

    def build(self):
        dbg(f"Running Bitbake with target image {self.target}...")
        docker.exec_cmd(f"bitbake {self.target}", self.container_name)

    def run(self, run_cmd):
        dbg(f"Running: {run_cmd}")
        docker.exec_cmd(run_cmd, self.container_name)

    def stop_container(self):
        dbg(f"Exiting container {self.container_name}")
        docker.stop_container(self.container_name)
