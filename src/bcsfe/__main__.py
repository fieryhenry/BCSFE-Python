from __future__ import annotations
import traceback

from bcsfe import cli, copy_to_data_dir

from bcsfe import core, __app_name__, __version__

import bcsfe
import argparse

from importlib import resources


def migrate(force: bool):
    v_path = core.Path.get_data_folder().add("version.txt")
    if not v_path.exists():
        try:
            v_path.write(core.Data(__version__))
        except FileNotFoundError:
            print(
                "Failed to create data folder. Something is wrong with your user's permissions or anti-virus software"
            )
            print("Please set the --data-dir flag to something the editor can write to")
            pass
        vers = None
    else:
        vers = v_path.read().to_str().strip()
    if vers != __version__ or force:
        p = resources.files(__app_name__).joinpath("files")
        copy_to_data_dir(p, p)
        v_path.write(core.Data(__version__))


def main():
    parser = argparse.ArgumentParser(bcsfe.__app_name__)

    parser.add_argument(
        "--version", "-v", action="store_true", help="display the version and exit"
    )
    parser.add_argument(
        "--input-path", "-i", type=str, help="input path to save file to edit"
    )
    parser.add_argument(
        "--game-data-dir", "-g", type=str, help="path to store the game data to"
    )
    parser.add_argument(
        "--data-dir", "-d", type=str, help="path to store editor data to"
    )
    parser.add_argument(
        "--transfer-backup-path",
        type=str,
        help="path to save the backup SAVE_DATA after transfering to",
    )
    parser.add_argument(
        "--config-path",
        "-c",
        type=str,
        default=None,
        help=f"path to the config file. If unspecified defaults to {core.Config.get_config_path()}",
    )
    parser.add_argument(
        "--log-path",
        "-l",
        type=str,
        default=None,
        help=f"path to the log file. If unspecified defaults to {core.Logger.get_log_path()}",
    )
    parser.add_argument(
        "--force-migrate",
        action="store_true",
        help=f"copy all data from bcsfe/src/files to {core.Path.get_data_folder()}",
    )

    args = parser.parse_args()
    if args.version:
        print(bcsfe.__version__)
        exit()

    if args.config_path is not None:
        core.set_config_path(core.Path(args.config_path))

    if args.log_path is not None:
        core.set_log_path(core.Path(args.log_path))

    if args.transfer_backup_path is not None:
        core.set_transfer_backup_path(core.Path(args.transfer_backup_path))

    if args.game_data_dir is not None:
        core.set_game_data_path(core.Path(args.game_data_dir))

    if args.data_dir is not None:
        core.set_data_dir_path(core.Path(args.data_dir))

    migrate(args.force_migrate)

    core.core_data.init_data()

    try:
        cli.main.Main().main(args.input_path)
    except KeyboardInterrupt:
        cli.main.Main.leave()
    except Exception as e:
        tb = traceback.format_exc()
        cli.color.color_print_key(
            "error", error=e, version=bcsfe.__version__, traceback=tb
        )
        try:
            cli.main.Main.exit_editor()
        except Exception:
            pass
        except KeyboardInterrupt:
            pass


main()
