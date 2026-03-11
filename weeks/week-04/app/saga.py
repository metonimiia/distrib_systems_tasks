STATES = {"NEW", "PAID", "DONE", "CANCELLED"}

TRANSITIONS = {
    "NEW": {
        "PAY_OK": "PAID",
        "PAY_FAIL": "CANCELLED",
    },
    "PAID": {
        "COMPLETE": "DONE",
        "CANCEL": "CANCELLED",
    },
    "DONE": {},
    "CANCELLED": {
        "RETRY_CANCEL": "CANCELLED",
    },
}


def next_state(state: str, event: str) -> str:
    """Return next saga state for the given event.

    Raises:
        ValueError: if state or event is unsupported for this state.
    """
    if state not in STATES:
        raise ValueError(f"Unknown state: {state}")

    state_transitions = TRANSITIONS[state]
    if event not in state_transitions:
        raise ValueError(f"Unsupported event {event!r} for state {state!r}")

    return state_transitions[event]
