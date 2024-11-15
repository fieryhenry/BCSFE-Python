__version__ = "3.0.0b3"

from bcsfe import core, cli


__all__ = ["core", "cli"]


def run():
    from bcsfe import __main__

    __main__.main()
