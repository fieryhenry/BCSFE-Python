from __future__ import annotations
import traceback

from bcsfe import cli

import sys

import bcsfe


def main():
    args = sys.argv[1:]
    for arg in args:
        if arg.lower() in ["--version", "-v"]:
            print(bcsfe.__version__)
            exit()

    try:
        cli.main.Main().main()
    except KeyboardInterrupt:
        cli.main.Main.leave()
    except Exception as e:
        tb = traceback.format_exc()
        cli.color.ColoredText.localize("error", error=e, traceback=tb)
        try:
            cli.main.Main.exit_editor()
        except Exception:
            pass
        except KeyboardInterrupt:
            pass


main()
