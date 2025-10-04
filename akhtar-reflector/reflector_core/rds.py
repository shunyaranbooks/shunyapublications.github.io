from collections import deque

ALPHA_DEFAULT = 0.7

def init_metrics(window=6):
    return dict(
        window=window, tau=0.75, alpha=ALPHA_DEFAULT,
        rds_history=deque(maxlen=window), turns_above_tau=0, rds_window=0.0
    )

def rds_from_model(model, alpha=ALPHA_DEFAULT, max_depth=3):
    score = 0.0
    d = int(model.get("depth", 1))
    meta = float(model.get("user_meta", 0.0))
    for i in range(1, min(max_depth, d) + 1):
        w = alpha ** i
        layer = (meta * (0.5 + 0.5 * (i >= 3)))  # weight meta more at i>=3
        score += w * layer
    # clamp
    if score < 0.0: score = 0.0
    if score > 1.0: score = 1.0
    return score

def update_metrics(m, user, reply, model, tau, alpha):
    r = rds_from_model(model, alpha=alpha, max_depth=model.get("depth", 3))
    m["rds_history"].append(r)
    avg = sum(m["rds_history"]) / max(1, len(m["rds_history"]))
    m["rds_window"] = avg
    if avg >= tau:
        m["turns_above_tau"] += 1
    return dict(r=r, rds_window=avg, turns_above_tau=m["turns_above_tau"])
