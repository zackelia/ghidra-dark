"""Install Ghidra dark theme."""
import argparse
import fileinput
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.request import urlopen

from tcd_browser import TCDBrowser, TCD_LIST
from preferences import preferences


logger = logging.getLogger(__name__)


def is_ghidra_running() -> bool:
    """Check if `ghidrarun` is running.

    Returns:
        bool: If Ghidra is running.
    """
    if os.name == "nt":
        find_ghidra = "WMIC path win32_process get Commandline"
    else:
        find_ghidra = "ps -ax"
    out = subprocess.check_output(find_ghidra.split())
    logger.debug("Running %s", find_ghidra)
    if b"ghidrarun" in out.lower():
        return True
    return False


def get_ghidra_install_path(install_path: str = None) -> str:
    """Find the Ghidra install path by using `which`.

    Args:
        install_path (str, optional): Ghidra install path. Defaults to None.

    Returns:
        str: Ghidra install path.
    """
    if install_path:
        return install_path
    # Attempt to find the installation directory based on `ghidraRun`
    ghidra_run_path = shutil.which("ghidraRun")
    if not ghidra_run_path:
        return None
    return Path(ghidra_run_path).parents[0]


def get_ghidra_config_path(version: str, user: str = None) -> str:
    """Find the Ghidra config path based off of `version` and `user`.

    Args:
        version (str): The current version of Ghidra.
        user (str, optional): The user's home to search. Defaults to None.

    Returns:
        str: Ghidra config path.
    """
    if user:
        home = os.path.expanduser(f"~{user}")
    else:
        home = Path.home()
    logger.debug("Using home: %s", home)

    # _PUBLIC was appended to the name after 9.0.4
    # The "-" after .ghidra was changed to "_" after 9.0.4
    version_number = ".".join(re.findall("[0-9]+", version))
    if tuple(map(int, (version_number.split(".")))) > (9, 0, 4):
        version_path = f".ghidra_{version}_PUBLIC"
        # _DEV when built from source, or from some repos (Arch, Kali, etc.)
        if not os.path.exists(os.path.join(home, ".ghidra", version_path)):
            version_path = f".ghidra_{version}_DEV"
    else:
        version_path = f".ghidra-{version}"

    return os.path.join(home, ".ghidra", version_path)


def get_ghidra_version(install_path: str) -> str:
    """Parse the version from the `application.properties` file.

    Args:
        install_path (str): Ghidra installation path; contains `application.properties`

    Returns:
        str: Ghidra Version (e.g. 9.2, 10.0-BETA).
    """
    # Get the version from the application.properties file
    properties_path = os.path.join(install_path, "Ghidra", "application.properties")
    with open(properties_path, "r") as fp:
        for line in fp:
            if "application.version=" in line:
                return line.split("=")[-1].strip()
    return ""


def install_flatlaf(
    install_path: str,
    version: str,
):
    """Download (if necessary) and install FlatLaf.

    Args:
        install_path (str): Ghidra install path.
        version (str): Current Ghidra Version.
    """
    # TODO: Refactor this duplicate code
    version_number = ".".join(re.findall("[0-9]+", version))
    version_number = tuple(map(int, (version_number.split("."))))
    if os.name == "nt":
        launch_sh = "launch.bat"
        # Missing quotes were added in 10.0
        if version_number < (10, 0, 0):
            install_dir = ";%INSTALL_DIR%"
            cpath = "set CPATH="
        else:
            install_dir = ";%INSTALL_DIR%\\"
            cpath = 'set "CPATH='
    else:
        launch_sh = "launch.sh"
        install_dir = ":${INSTALL_DIR}/"
        cpath = "CPATH="

    flatlaf_version = "0.43"
    flatlaf_path = os.path.join(install_path, f"flatlaf-{flatlaf_version}.jar")
    flatlaf_url = (
        f"https://repo1.maven.org/maven2/com/formdev/flatlaf/{flatlaf_version}/"
        f"flatlaf-{flatlaf_version}.jar"
    )

    # Download the FlatLaf jar
    if not os.path.exists(flatlaf_path):
        logging.debug("Downloading FlatLaf")
        with urlopen(flatlaf_url) as connection:
            with open(flatlaf_path, "wb") as fp:
                fp.write(connection.read())
    else:
        logging.debug("Flatlaf already downloaded: %s", flatlaf_path)

    launch_sh_path = os.path.join(install_path, "support", launch_sh)
    launch_properties_path = os.path.join(install_path, "support", "launch.properties")

    # Add FlatLaf to the list of jar files
    with fileinput.FileInput(launch_sh_path, inplace=True, backup=".bak") as fp:
        for line in fp:
            if line.strip().startswith(cpath) and "flatlaf" not in line:
                if os.name == "nt" and version_number < (10, 0, 0):
                    print(f"{line.rstrip()}{install_dir}flatlaf-{flatlaf_version}.jar")
                else:
                    print(
                        f'{line.rstrip()[:-1]}{install_dir}flatlaf-{flatlaf_version}.jar"'
                    )
            else:
                print(line, end="")

    # Check if FlatLaf is the system L&f
    flatlaf_set = False
    with open(launch_properties_path, "r") as fp:
        for line in fp:
            if "flatlaf" in line:
                flatlaf_set = True
                break

    # Set FlatLaf as the system L&f
    if not flatlaf_set:
        with open(launch_properties_path, "a") as fp:
            logging.debug("Setting FlatLaf as system L&f")
            fp.write("\nVMARGS=-Dswing.systemlaf=com.formdev.flatlaf.FlatDarkLaf")


def install_dark_preferences(config_path: str):
    """Backup and modify preference files to use dark colors.

    Args:
        config_path (str): Ghidra config path.
    """
    preferences_path = os.path.join(config_path, "preferences")
    if not os.path.exists(preferences_path):
        logging.error("Please open Ghidra at least once to fully install dark mode.")
        sys.exit(-1)

    # Check if the current L&f is system
    using_system = False
    with open(preferences_path, "r") as fp:
        for line in fp:
            if "LastLookAndFeel=System" in line:
                using_system = True
                break

    # Set the L&f to system
    if not using_system:
        with open(preferences_path, "a") as fp:
            fp.write("LastLookAndFeel=System\n")

    # Backup and modify the current tcd and tool files
    for tcd in TCD_LIST:
        tcd_path = os.path.join(config_path, "tools", tcd)
        backup_path = os.path.join(config_path, "tools", f"{tcd}.bak")
        try:
            shutil.copy(tcd_path, backup_path)
            browser = TCDBrowser(tcd_path)
            browser.update(preferences)
        except FileNotFoundError:
            if tcd == "_code_browser.tcd":
                logging.warning(
                    "Please open Ghidra at least once to fully install dark mode."
                )
            else:
                logging.debug("Could not open %s", tcd)


def main(args: argparse.Namespace):
    """Install Ghidra dark theme

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

    logging.debug("Installing FlatLaf...")
    install_flatlaf(ghidra_install_path, ghidra_version)

    logging.debug("Installing dark preferences...")
    install_dark_preferences(ghidra_config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Ghidra dark theme")
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
