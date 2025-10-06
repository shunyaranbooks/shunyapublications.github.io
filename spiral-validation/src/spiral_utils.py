import re
from typing import Dict

KEYWORDS = {
    'clarifying': ['what do we mean', 'define', 'clarify', 'example of'],
    'causal': ['why', 'cause', 'because', 'due to'],
    'ethical': ['should', 'fair', 'ethical', 'moral', 'who benefits', 'who is harmed'],
    'transformational': ['how might', 'redesign', 'reimagine', 'what if we'],
    'meta': ['assumption', 'what are we not', 'blind spot', 'why are we asking']
}

def layer_scores(text: str) -> Dict[str, float]:
    t = text.lower()
    scores = {}
    for layer, kws in KEYWORDS.items():
        scores[layer] = 1.0 if any(re.search(re.escape(k), t) for k in kws) else 0.0
    return scores
