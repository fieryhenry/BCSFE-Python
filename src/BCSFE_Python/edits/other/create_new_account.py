"""Handler for creating a new account"""

from typing import Any

from . import fix_elsewhere
from ... import helper, server_handler


def create_new_account(save_stats: dict[str, Any]):
    """Create a new account"""

    helper.colored_text("Creating a new account...", helper.GREEN)

    save_stats["inquiry_code"] = server_handler.get_inquiry_code()
    save_stats["token"] = "0" * 40
    save_stats = fix_elsewhere.fix_elsewhere(save_stats, force_mi=True)

    return save_stats
