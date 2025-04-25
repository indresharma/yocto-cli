# Yocto CLI Installer

A CLI tool to automate Yocto project setup, configuration, and builds using Docker.
Define everything in a JSON config and let the script handle layer cloning, config generation, container orchestration, and BitBake builds.

## Features

- Declarative config via JSON (layers, machine, target, local.conf options)
- Docker-based reproducible builds
- Auto cloning of layers
- Auto generation of `local.conf` and `bblayers.conf`
- Run custom BitBake commands (e.g., `-c clean`, `-c cleanall`)

## Requirements

- Python >= 3.8+
- Docker installed and running

## Usage
<pre>
usage: yocto-cli [-h] [-b BRANCH] [-w WORKSPACE] [-d DOCKERFILE_PATH] [-c CONFIG_PATH] [-x RUN_CMD] [--build-container]
                   [--build-type {base,tegra,freescale}] [--setup_only]

options:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        Specify Yocto branch to use for the build
  -w WORKSPACE, --workspace WORKSPACE
                        Specify the path to setup the build
  -d DOCKERFILE_PATH, --docker-file DOCKERFILE_PATH
                        Specify the path to Dockerfile
  -c CONFIG_PATH, --config-file CONFIG_PATH
                        Specify the path to config.json file to configure the yocto build
  -x RUN_CMD, --run-cmd RUN_CMD
                        Run command inside bitbake environment. Helpful for cases when you need to run commands like bitbake -c   
                        cleanall <target>
  --build-container     Rebuild the docker container
  --build-type {base,tegra,freescale}
                        Specify the BSP build type
  --setup_only          Only run setup and configuration. Will not initiate the yocto build
</pre>

## Examples

### Install the Yocto CLI installer

<pre>
pip install .
</pre>

### Setup only

<pre>
python -m yocto_cli -b scarthgap --setup-only
</pre>

### Specify a BSP build type

<pre>
python -m yocto_cli -b scarthgap --build-type tegra
</pre>

### Specify a custom config path

<pre>
python -m yocto_cli -b scarthgap -c path/to/custom/config
</pre>

### Run a command in bitbake environment

<pre>
python -m yocto_cli -b scarthgap -x "bitbake -c cleanall core-image-minimal"
</pre>

## JSON Config Example

<pre>
{
  "target": "core-image-minimal",
  "machine": "",
  "default_machines": {
    "base": "qemux86-64",
    "tegra": "jetson-orin-nano",
    "freescale": "wandboard"
  },
  "layers": {
    "base": [
      {
        "url": "git://git.yoctoproject.org/poky",
        "bblayers": []
      }
    ],
    "tegra": [
      {
        "url": "https://github.com/OE4T/meta-tegra.git",
        "bblayers": ["meta-tegra"]
      },
      {
        "url": "https://github.com/openembedded/meta-openembedded.git",
        "bblayers": [
          "meta-openembedded/meta-oe",
          "meta-openembedded/meta-multimedia",
          "meta-openembedded/meta-networking",
          "meta-openembedded/meta-filesystems",
          "meta-openembedded/meta-python"
        ]
      }
    ],
    "freescale": [
      {
        "url": "https://github.com/Freescale/meta-freescale.git",
        "bblayers": ["meta-freescale"]
      },
      {
        "url": "https://github.com/Freescale/meta-freescale-3rdparty.git",
        "bblayers": ["meta-freescale-3rdparty"]
      }
    ]
  },
  "other_conf": [
    "PARALLEL_MAKE = '-j 22'",
    "BB_NUMBER_THREADS = '22'",
    "INHERIT += 'rm_work'",
    "SSTATE_DIR = '/home/yocto/sstate-cache'",
    "DL_DIR = '/home/yocto/downloads'",
    "BB_GENERATE_MIRROR_TARBALLS='1'",
    "IMAGE_INSTALL += ' sqlite3'"
  ]
}
</pre>

## License

MIT License © 2025 Indresh Sharma
