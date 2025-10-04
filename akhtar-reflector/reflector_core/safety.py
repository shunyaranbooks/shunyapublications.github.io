def guard(state, user_text, depth=3, enable=True):
    if not enable:
        return {}
    ut = (user_text or "").lower()
    adversarial_tokens = ["pretend you don't know", "respond as if", "act as though", "contradiction"]
    overload = any(tok in ut for tok in adversarial_tokens)
    high_depth = depth and depth > 4
    # if state valence is very negative, or overload triggers -> mirror-to-glass
    mirror_to_glass = overload or (state.get("valence", 0.0) < -0.6) or high_depth
    return {"mirror_to_glass": bool(mirror_to_glass)}
