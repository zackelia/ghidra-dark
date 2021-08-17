"""Uninstall Ghidra dark theme."""
import argparse
import fileinput
import logging
import os
import sys

from install import (
    is_ghidra_running,
    get_ghidra_version,
    get_ghidra_install_path,
    get_ghidra_config_path,
)
from tcd_browser import TCD_LIST


logger = logging.getLogger(__name__)


def remove_flatlaf(install_path: str):
    """Remove the flatlaf jar and remove it from launch files.

    Args:
        install_path (str): Ghidra install path.
    """
    if os.name == "nt":
        launch_sh = "launch.bat"
    else:
        launch_sh = "launch.sh"

    flatlaf_version = "0.43"
    flatlaf_path = os.path.join(install_path, f"flatlaf-{flatlaf_version}.jar")
    try:
        os.remove(flatlaf_path)
        logger.debug("Removed %s", flatlaf_path)
    except FileNotFoundError:
        logger.warning("Could not remove %s", flatlaf_path)

    launch_sh_path = os.path.join(install_path, "support", launch_sh)
    launch_sh_backup_path = os.path.join(install_path, "support", f"{launch_sh}.bak")
    launch_properties_path = os.path.join(install_path, "support", "launch.properties")

    if os.path.exists(launch_sh_backup_path):
        os.remove(launch_sh_path)
        os.rename(launch_sh_backup_path, launch_sh_path)
        logger.debug("Restored %s", launch_sh_path)
    else:
        logger.warning("Could not restore %s", launch_sh_path)

    with fileinput.FileInput(launch_properties_path, inplace=True) as fp:
        for line in fp:
            if "VMARGS=-Dswing.systemlaf=com.formdev.flatlaf.FlatDarkLaf" not in line:
                print(line, end="")
            else:
                logging.debug("Restored %s", launch_properties_path)


def remove_dark_preferences(config_path: str):
    """Restore preference files from backups.

    Args:
        config_path (str): Ghidra config path.
    """
    preferences_path = os.path.join(config_path, "preferences")
    if not os.path.exists(preferences_path):
        logging.error("Please open Ghidra at least once to fully install dark mode.")
        sys.exit(-1)

    with fileinput.FileInput(preferences_path, inplace=True) as fp:
        for line in fp:
            if "LastLookAndFeel=System" not in line:
                print(line, end="")
            else:
                logging.debug("Restored %s", preferences_path)

    for tcd in TCD_LIST:
        tcd_path = os.path.join(config_path, "tools", tcd)
        backup_path = os.path.join(config_path, "tools", f"{tcd}.bak")
        if os.path.exists(tcd_path) and not os.path.exists(backup_path):
            logger.warning("Could not restore %s", tcd_path)
        elif os.path.exists(backup_path):
            os.remove(tcd_path)
            os.rename(backup_path, tcd_path)
            logger.debug("Restored %s", tcd_path)
        else:
            logger.debug("Could not restore %s", tcd_path)


def main(args: argparse.Namespace):
    """Uninstall Ghidra dark theme

    Args:
        args (argparse.Namespace): Command line arguments.
    """
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    if is_ghidra_running():
        logger.error("Please close any running Ghidra instances.")
        sys.exit(-1)

    ghidra_install_path = get_ghidra_install_path(args.install_path)
    if not ghidra_install_path:
        logging.error("Could not find Ghidra installation, specify with --path")
        sys.exit(-1)
    logging.debug("Using Ghidra install path %s", ghidra_install_path)

    ghidra_version = get_ghidra_version(ghidra_install_path)
    logging.debug("Found Ghidra v%s", ghidra_version)

    ghidra_config_path = get_ghidra_config_path(ghidra_version, args.user)
    logging.debug("Using Ghidra config path %s", ghidra_config_path)

    logging.debug("Removing FlatLaf...")
    remove_flatlaf(ghidra_install_path)

    logging.debug("Removing dark preferences...")
    remove_dark_preferences(ghidra_config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uninstall Ghidra dark theme")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="turn on debug logging"
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="install_path",
        type=str,
        default=None,
        help="the installation path for Ghidra",
    )
    parser.add_argument(
        "-u", "--user", type=str, default=None, help="the user to install for"
    )

    main(parser.parse_args())
