# History

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org/).

### 0.2.0 (2025-11-13)

- ADDED - Allow `Service` to accept a `state_change_callback` which is called when the `is_running` status changes (if monitoring).

### 0.1.9 (2025-11-10)

- ADDED - Remove log event for `ScheduledTask` commands. Too verbose.
- ADDED - On macOS, "ask" the app to quit gracefully via `osascript`, then if it does not, force kill the process via `psutil`. This addresses an issue where apps like TeamViewer, which have watchdog processes, will try to restart the app if killed via `SIGTERM/SIGKILL`.
- FIXED - Bug with invalidating stale PID/Process cache
- ADDED - Allow `NativeApp` and `TeamViewer` to accept a `state_change_callback` which is called when the `is_running` status changes (if monitoring).

### 0.1.8 (2025-11-04)

- ADDED - `ScheduledTask` basic control (start, stop) for Windows only.

### 0.1.7 (2025-10-10)

- ADDED - Added `UnityApp` class which is just an extended `NativeApp` class with some additional getters to make things easier when working with Unity builds.
- Added `last_seen` to `process_info` for `Service` and `NativeApp`

## 0.1.6 (2025-10-02)

- CHANGED - `Service` class on Mac/Linux defaults to `supervisorctl`
- ADDED - If you want to use `systemctl` on Linux you can do `from process_inspector.servicecontrol import service_class_factory` and then instantiate with `Service = service_class_factory('systemctl')`.

## 0.1.5 (2025-09-29)

- CHANGED - `get_process_info` can fail if the process was killed by the user within Windows/Mac. This fix handles that by resetting the cache so the process is looked up again.

## 0.1.4 (2025-09-23)

- CHANGED - Fixed failing Linux tests

## 0.1.3 (2025-09-16)

- CHANGED - Improved query times for process running and process info

## 0.1.2 (2025-09-11)

- ADDED - Service control (Windows Services or Linux/ Mac `supervisorctl` processes)
- ADDED - TeamViewer status and basic control (start, stop)

## 0.1.1 (2025-09-11)

- ADDED - more test coverage

## 0.1.0 (2025-09-11)

- First release
