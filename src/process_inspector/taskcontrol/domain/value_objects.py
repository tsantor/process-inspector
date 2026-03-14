TASK_STATE_MAP = {
    0: "UNKNOWN",
    1: "DISABLED",
    2: "QUEUED",
    3: "READY",
    4: "RUNNING",
}


def map_task_state(state_index) -> str:
    return TASK_STATE_MAP.get(state_index, "UNKNOWN")
