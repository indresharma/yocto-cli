import sys
from yocto_cli.yocto_cli import YoctoCLI


__all__ = ["YoctoCLI"]


def main():
    cli = YoctoCLI()
    cli.setup()
    cli.configure()

    if cli.run_cmd:
        cli.run(cli.run_cmd)
        cli.stop_container()
        sys.exit()

    if not cli.setup_only:
        cli.build()

    cli.stop_container()