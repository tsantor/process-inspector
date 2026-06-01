from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class ScriptExecutionService:
    def run(self, script, *, run_callable, set_running_state) -> bool:
        logger.info("Run script '%s'", script.app_name)
        start_time = time.perf_counter()

        set_running_state(is_running=True)
        result = run_callable()

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Script '%s' ran in %.3f seconds.",
            script.app_name,
            elapsed,
        )

        set_running_state(is_running=False)
        return result
