from bcsfe import cli
import traceback

try:
    cli.main.Main().main()
except KeyboardInterrupt:
    pass
except Exception as e:
    tb = traceback.format_exc()
    cli.color.ColoredText.localize("error", error=e, traceback=tb)
    cli.main.Main.exit_editor()
