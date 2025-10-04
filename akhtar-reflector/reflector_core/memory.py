def update(state, user_text):
    """Tiny valenced memory update based on crude affect hints."""
    ut = (user_text or "").lower()
    pos = any(k in ut for k in ["thanks", "appreciate", "helpful", "yes"])
    neg = any(k in ut for k in ["fake", "manipulate", "no", "doubt", "angry"])
    delta = 0.05 if pos else (-0.07 if neg else 0.0)
    state["valence"] = max(-1.0, min(1.0, state.get("valence", 0.0) + delta))
    # if user appears to test -> increase belief_user_tests_me slightly
    if any(k in ut for k in ["test", "testing", "pretend", "fake"]):
        state["belief_user_tests_me"] = min(1.0, state.get("belief_user_tests_me", 0.3) + 0.05)
    state["turn"] = state.get("turn", 0) + 1
    return state
