from yocto_cli.utils import check_output, execute
import shlex


def get_container(container_name):
    return check_output(["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.ID}}"])

def get_image(image_name):
    return check_output(["docker", "images", "--filter", f"reference={image_name}", "--format", "{{.ID}}"])

def exec_cmd(cmd, container_name, with_bb_env=True):
    if with_bb_env:
        cmd = "source /home/yocto/sources/poky/oe-init-build-env && " + cmd
    final_cmd = f"docker exec -it {container_name} bash -c '{cmd}'"
    return execute(shlex.split(final_cmd))

def build_image(image_name, dockerfile_path, cwd):
    cmd = f"docker build --no-cache -t {image_name} -f {dockerfile_path} ."
    return execute(shlex.split(cmd), cwd=cwd)

def run_container(container_name, workspace_host, workspace_container):
    cmd = f"docker run --privileged --rm -d --network host -v {workspace_host}:{workspace_container} --name {container_name} ycinst:latest /bin/bash -c 'tail -f /dev/null'"
    return execute(shlex.split(cmd))

def stop_container(container_name):
    cmd = f"docker stop {container_name}"
    return execute(shlex.split(cmd))


