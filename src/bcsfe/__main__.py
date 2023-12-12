import traceback

from bcsfe import cli

import sys

args = sys.argv[1:]
if len(args) > 0:
    if args[0].strip() == "ui":
        from bcsfe import ui

        ui.main.run()

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
