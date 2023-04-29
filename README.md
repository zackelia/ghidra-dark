# ghidra-dark

[![Ghidra 9.0-10.2.3](https://img.shields.io/badge/Ghidra-9.0--10.2.3-red)](https://github.com/NationalSecurityAgency/ghidra/releases)
[![Python >=3.6](https://img.shields.io/badge/python->=3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

> **Warning**
> Ghidra >=10.3 not supported. Check out [ghidra-dark-theme](https://github.com/zackelia/ghidra-dark-theme) instead!

ghidra-dark provides a simple to use script to install the FlatLaf dark theme, custom colors for disassembly/decompilation in Ghidra, and some other helpful settings. A script is also provided for uninstallation. The scripts officially support all public builds through version 10.2.3 on Windows, Linux, and macOS.

## Install

```
$ python3 install.py
```

If installing as root (e.g. `sudo`), the user to install for may need to be specified:

```
$ sudo python3 install.py -u [user]
```

![](ghidra-dark.png)

## Uninstall

```
$ python3 uninstall.py
```
