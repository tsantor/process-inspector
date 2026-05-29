# History

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org/).

### 0.2.8 (2026-05-29)

- CHANGED - Hardened process snapshot collection path in `get_process_info` for lower heartbeat latency on Linux/Raspberry Pi by reusing values within a single `oneshot()` snapshot.
- CHANGED - Removed duplicate expensive psutil getter calls within one snapshot (single `memory_info()` reuse for `mem_usage`/`vmem_usage`, single `create_time()` reuse for uptime fields).
- CHANGED - Made CPU usage collection explicit and non-blocking via `cpu_percent(interval=None)` in process snapshot output, preserving existing `proc_usage` format.
- CHANGED - Simplified `get_process_info` internals by removing temporary timing instrumentation while keeping the latency-focused optimizations.
- ADDED - Targeted processutils tests covering CPU call semantics (`interval=None`) and no-duplicate-call behavior in snapshot assembly.

### 0.2.7 (2026-05-22)

- CHANGED - Reduced Linux service polling overhead by reusing cached read results in supervisor/systemctl service control paths and avoiding redundant status/pid subprocess calls per read cycle.
- CHANGED - Consolidated Linux `systemctl` read flow to a single cached `show` source for status and PID resolution, preserving existing status/running semantics.
- CHANGED - Tuned Linux supervisor read-cache TTL for real polling cadence to reduce repeated expensive status calls between adjacent poll windows.
- CHANGED - Removed temporary service command aggregation debug instrumentation after validation to keep runtime logs clean.
- ADDED - Expanded targeted servicecontrol tests covering read-path subprocess call-count reduction, cache-hit behavior, cache invalidation after lifecycle/reset actions, and status/running compatibility.

### 0.2.6 (2026-04-20)

- CHANGED - Updated build tooling stack and lock/config wiring for the current release workflow.
- CHANGED - Refined `just` release/development commands and aligned README command references with the updated task flow.
- CHANGED - Refreshed public API snapshot/contract support files as part of the build tooling update.

### 0.2.5 (2026-03-14)

- CHANGED - Continued DDD/SOA/SRP refactor pass across subdomains with stricter layer boundaries and architecture guard tests for import direction.
- CHANGED - Rebalanced platform-specific execution concerns into infrastructure adapters (`appcontrol`/`scriptcontrol`) and removed internal shim-style imports in favor of direct internal module imports.
- CHANGED - Standardized DTO usage in `servicecontrol` and tightened interface schema definitions for clearer, explicit contracts.
- CHANGED - Centralized TeamViewer platform wiring in infrastructure factory composition.
- FIXED - Release pipeline now passes strict lint/test gates and builds validated `sdist`/`wheel` artifacts for this version.

### 0.2.4 (2026-03-14)

- CHANGED - Refactored subdomains into layered DDD/SRP structure (`domain`, `application`, `infrastructure`, `interface`) while preserving public API contract symbols.
- ADDED - Contract-driven release checks for public API stability via `api/public_api.contract.json` and snapshot verification.
- ADDED - Expanded test coverage for layered subdomain services and adapters.
- CHANGED - Updated README development/testing workflow to use `just` commands instead of legacy `make` commands.

### 0.2.3 (2025-12-09)

- FIXED - Wrong Service **init** signature for Windows.

### 0.2.2 (2025-12-03)

- ADDED - More test coverage and tox
- ADDED - `Script` basic control (run) of a script file. Currently only supports bash on Mac/Linux and Powershell on Windows.

### 0.2.1 (2025-11-26)

- FIXED - Correctly return false if invalid app name on Mac

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
