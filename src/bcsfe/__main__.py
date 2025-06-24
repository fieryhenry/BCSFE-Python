from __future__ import annotations
import traceback

from bcsfe import cli


import bcsfe
import argparse

def main():
    parser = argparse.ArgumentParser("bcsfe")

    parser.add_argument("--version", "-v", action="store_true", help="display the version and exit")
    parser.add_argument("--input-path", "-i", type=str, help="input path to save file to edit")

    args = parser.parse_args()
    if args.version:
        print(bcsfe.__version__)
        exit()

    try:
        cli.main.Main().main(args.input_path)
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
