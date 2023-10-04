import traceback

from bcsfe import cli

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
