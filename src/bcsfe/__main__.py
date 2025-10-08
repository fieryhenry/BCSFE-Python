from __future__ import annotations
import traceback

from bcsfe import cli

from bcsfe import core

import bcsfe
import argparse


def main():
    parser = argparse.ArgumentParser("bcsfe")

    parser.add_argument(
        "--version", "-v", action="store_true", help="display the version and exit"
    )
    parser.add_argument(
        "--input-path", "-i", type=str, help="input path to save file to edit"
    )
    parser.add_argument(
        "--config-path",
        "-c",
        type=str,
        default=None,
        help="path to the config file. If unspecified defaults to Documents/bcsfe/config.yaml",
    )
    parser.add_argument(
        "--log-path",
        "-l",
        type=str,
        default=None,
        help="path to the log file. If unspecified defaults to Documents/bcsfe/bcsfe.log",
    )

    args = parser.parse_args()
    if args.version:
        print(bcsfe.__version__)
        exit()

    if args.config_path is not None:
        core.set_config_path(core.Path(args.config_path))

    if args.log_path is not None:
        core.set_log_path(core.Path(args.log_path))

    core.core_data.init_data()

    try:
        cli.main.Main().main(args.input_path)
    except KeyboardInterrupt:
        cli.main.Main.leave()
    except Exception as e:
        tb = traceback.format_exc()
        cli.color.ColoredText.localize(
            "error", error=e, version=bcsfe.__version__, traceback=tb
        )
        try:
            cli.main.Main.exit_editor()
        except Exception:
            pass
        except KeyboardInterrupt:
            pass


main()
