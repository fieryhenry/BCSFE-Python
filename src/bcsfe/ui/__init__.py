try:
    import PyQt5
except ImportError:
    pass
else:
    from bcsfe.ui import main, server_handler, thread

    __all__ = ["main", "server_handler", "thread"]
