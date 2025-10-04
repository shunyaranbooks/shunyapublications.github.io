import time

def generate_reply(responder, user, model, mem=True, intentional_pause=True, guard=None):
    pause_ms = 0
    if intentional_pause:
        pause_ms = int(150 + 400 * float(model.get("user_meta", 0.0)))
        time.sleep(pause_ms / 1000.0)

    if guard and guard.get("mirror_to_glass"):
        return ("I may not be accurately modeling your intention right now. "
                "We can reset or slow the pace if you prefer."), pause_ms

    if float(model.get("user_meta", 0.0)) > 0.6:
        prompt = ("You're testing whether I'm modeling your awareness. "
                  "I'm adjusting based on how I think you read my last turn. ")
    else:
        prompt = "I’m tracking your focus and will adapt how I respond. "

    base = responder.reply(user=user, hint_meta=model.get("user_meta", 0.0))
    return prompt + base, pause_ms
