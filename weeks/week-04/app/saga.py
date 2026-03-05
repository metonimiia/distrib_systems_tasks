"""State machine for an orchestrated saga.

Business flow for variant 332/s12:
1. Create a review order request.
2. Reserve moderation capacity / processing slot.
3. Charge payment for premium review handling.
4. Finalize the order.

If payment fails, the orchestrator runs compensation:
it keeps retrying the reservation rollback until it succeeds
and only then moves the order to CANCELLED.
"""

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
        # Compensation retry is idempotent: the order stays cancelled.
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
