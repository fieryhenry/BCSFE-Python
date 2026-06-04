__version__ = "3.4.0"

__app_name__ = "bcsfe"

from importlib.resources.abc import Traversable

from bcsfe import core, cli


__all__ = ["core", "cli"]


def copy_to_data_dir(base_path: Traversable, path: Traversable):
    if path.is_dir():
        for item in path.iterdir():
            copy_to_data_dir(base_path, item)
    else:
        to_add = str(path).replace(str(base_path), "")
        if to_add.startswith("/"):
            to_add = to_add[1:]
        new_path = core.Path.get_data_folder().add(to_add)
        data = path.read_bytes()

        new_path.parent().generate_dirs()

        new_path.write(core.Data(data))


def run():
    from bcsfe import __main__

    __main__.main()
