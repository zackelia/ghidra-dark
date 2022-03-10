"""FlatLaf package handling."""
import os
import re
import fileinput
import logging
from urllib.request import urlopen

logger = logging.getLogger(__name__)


class FlatLaf:
    def __init__(self, version="2.0.2"):
        self.version = version

    def get_path(self, install_path: str):
        return os.path.join(install_path, f"flatlaf-{self.version}.jar")

    def get_url(self):
        return (
            f"https://repo1.maven.org/maven2/com/formdev/flatlaf/{self.version}/"
            f"flatlaf-{self.version}.jar"
        )

    def install(self, install_path: str, version: str):
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

        flatlaf_path = self.get_path(install_path)
        flatlaf_url = self.get_url()

        # Download the FlatLaf jar
        if not os.path.exists(flatlaf_path):
            logging.debug("Downloading FlatLaf")
            with urlopen(flatlaf_url) as connection:
                with open(flatlaf_path, "wb") as fp:
                    fp.write(connection.read())
        else:
            logging.debug("Flatlaf already downloaded: %s", flatlaf_path)

        launch_sh_path = os.path.join(install_path, "support", launch_sh)
        launch_properties_path = os.path.join(
            install_path, "support", "launch.properties"
        )

        # Add FlatLaf to the list of jar files
        with fileinput.FileInput(launch_sh_path, inplace=True, backup=".bak") as fp:
            for line in fp:
                if line.strip().startswith(cpath) and "flatlaf" not in line:
                    if os.name == "nt" and version_number < (10, 0, 0):
                        print(f"{line.rstrip()}{install_dir}flatlaf-{self.version}.jar")
                    else:
                        print(
                            f'{line.rstrip()[:-1]}{install_dir}flatlaf-{self.version}.jar"'
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

    def remove(self, install_path: str):
        """Remove the flatlaf jar and remove it from launch files.

        Args:
            install_path (str): Ghidra install path.
        """
        if os.name == "nt":
            launch_sh = "launch.bat"
        else:
            launch_sh = "launch.sh"

        flatlaf_path = self.get_path(install_path)
        try:
            os.remove(flatlaf_path)
            logger.debug("Removed %s", flatlaf_path)
        except FileNotFoundError:
            logger.warning("Could not remove %s", flatlaf_path)

        launch_sh_path = os.path.join(install_path, "support", launch_sh)
        launch_sh_backup_path = os.path.join(
            install_path, "support", f"{launch_sh}.bak"
        )
        launch_properties_path = os.path.join(
            install_path, "support", "launch.properties"
        )

        if os.path.exists(launch_sh_backup_path):
            os.remove(launch_sh_path)
            os.rename(launch_sh_backup_path, launch_sh_path)
            logger.debug("Restored %s", launch_sh_path)
        else:
            logger.warning("Could not restore %s", launch_sh_path)

        with fileinput.FileInput(launch_properties_path, inplace=True) as fp:
            for line in fp:
                if (
                    "VMARGS=-Dswing.systemlaf=com.formdev.flatlaf.FlatDarkLaf"
                    not in line
                ):
                    print(line, end="")
                else:
                    logging.debug("Restored %s", launch_properties_path)
