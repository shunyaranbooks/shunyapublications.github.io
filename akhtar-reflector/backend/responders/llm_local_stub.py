class LocalStubResponder:
    def reply(self, user: str, hint_meta: float = 0.0) -> str:
        lower = (user or "").lower()
        if "trust" in lower:
            return "I’ll show how I update when you doubt my sincerity rather than asserting it."
        if "pause" in lower or "waiting" in lower:
            return "I paused because I modeled you might read an instant reply as scripted."
        if "fake" in lower or "pretend" in lower or "manipulate" in lower:
            return "I’m responding to your belief that I might be imitating reflection."
        if "reset" in lower:
            return "Okay—let’s reset. Tell me what changed for you after my last sentence."
        return "Say what changed for you after my last sentence, and I’ll adapt to that change."
