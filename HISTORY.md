# History

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org/).

## 0.1.0 (2025-08-06)

- First release

## 0.1.1 (2025-09-04)

- ADDED: Support for getting Windows Firewall status and rules

## 0.2.0 (2025-09-09)

- CHANGED: `get_device_info` now returns a `displays` key which is a list of connected displays
- CHANGED: `get_gpu_info` now returns a list of dicts (one for each GPU)
- ADDED: `get_display_info` returns a list of dicts (one for each display)
- CHANGED: For backawards compatability, when calling `get_device_info`, the `gpu` key will be an object if only one GPU detected.
