# Process Inspector

![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)

## Overview

A Python package for cross-platform process management, providing process data as dicts/JSON and allowing process control (start, stop, kill) on Windows, Mac, and Linux.

## Installation

Use `uv` or `pip`.

```bash
uv pip install process-inspector
python3 -m pip install process-inspector
```

## Development

To get a list of all commands with descriptions simply run `make`.

```bash
make env
make pip_install_editable
```

## Testing

```bash
make pytest
make coverage
make open_coverage
```

## Issues

If you experience any issues, please create an [issue](https://github.com/tsantor/process-inspector/issues) on Github.

## Example Usage

```python
from process_inspector import NativeApp
from process_inpsector import OperatingSystem

# This operation requires sudo priveleges on Linux and Mac so ensure you allow it for the user the application is running under.
OperatingSystem().reboot()
```
