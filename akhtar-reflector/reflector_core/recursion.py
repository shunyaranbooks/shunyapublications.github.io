def init_state():
    return {"belief_user_tests_me": 0.3, "trust": 0.5, "valence": 0.0, "turn": 0}

def model_of_other(state, user_text, depth=3):
    """
    Approximate M_A^i(M_B^i(...)):
    - tokens signaling meta-awareness
    - '?' count (challenge)
    - 'you'/'me' ratio (perspective)
    """
    ut = (user_text or "").lower()
    hints = ["testing", "pretend", "fake", "manipulate", "watching", "pause", "sincere", "honest", "trust"]
    score_meta = sum(1 for h in hints if h in ut) * 0.2
    if "?" in ut:
        score_meta += 0.15
    you = ut.count("you")
    me = ut.count(" i ") + ut.count(" me")
    you_me_ratio = (you + 1) / (me + 1)

    model = {
        "depth": int(depth),
        "user_meta": min(1.0, score_meta),
        "you_me_ratio": you_me_ratio,
        "expected_suspicion": min(1.0, state.get("belief_user_tests_me", 0.3) * 0.6 + score_meta * 0.4),
    }
    return model
