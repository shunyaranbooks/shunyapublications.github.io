from collections import Counter
import pandas as pd
import ast, re
from typing import List, Dict

# Canonical layers
LAYERS = ["Clarifying", "Causal", "Ethical", "Transformational", "Meta"]
_CANON = {
    "clarifying": "Clarifying",
    "causal": "Causal",
    "ethical": "Ethical",
    "transformational": "Transformational",
    "meta": "Meta",
}

# ---- helpers ---------------------------------------------------------------

def _canonize(s: str) -> str | None:
    """Map many spellings/phrases to a canonical layer, else None."""
    if not s:
        return None
    k = s.strip().strip("'\"").lower()

    # direct hits
    if k in _CANON:
        return _CANON[k]

    # light synonyms / fuzzy starts
    if k.startswith("clarif") or "define" in k or "what do we mean" in k:
        return "Clarifying"
    if k.startswith("cause") or k == "why" or "because" in k:
        return "Causal"
    if k.startswith("ethic") or k.startswith("should") or "fair" in k or "harm" in k:
        return "Ethical"
    if k.startswith("transform") or "reimagin" in k or "redesign" in k or "how might" in k:
        return "Transformational"
    if k == "meta" or "assumption" in k or "what are we not" in k or "frame" in k:
        return "Meta"
    return None


_SPLIT_RE = re.compile(r"[;,|/]+|,\s*")

def _norm_labels(val) -> List[str]:
    """
    Accepts: list like ['Clarifying'], JSON-ish string "['Clarifying']",
    or delimited string 'Clarifying, Causal'. Returns canonical layer list.
    """
    raw: List[str] = []
    if isinstance(val, list):
        raw = [str(x) for x in val]
    elif isinstance(val, str):
        s = val.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    raw = [str(x) for x in parsed]
                else:
                    raw = [s]
            except Exception:
                raw = [s]
        else:
            raw = [x for x in _SPLIT_RE.split(s) if x.strip()]
    else:
        raw = []

    out = []
    for x in raw:
        c = _canonize(x)
        if c:
            out.append(c)
    # dedupe while preserving order
    seen = set()
    uniq = [x for x in out if not (x in seen or seen.add(x))]
    return uniq


# Optional fallback: infer a layer from the text if labels are missing
def _infer_from_text(text: str) -> List[str]:
    t = (text or "").lower()
    labs = []
    if re.search(r"\bwhat do we mean|define|clarif|example|difference\b", t):
        labs.append("Clarifying")
    if re.search(r"\bwhy\b|cause|driver|because", t):
        labs.append("Causal")
    if re.search(r"\bshould\b|fair|just|ethic|who benefits|harm", t):
        labs.append("Ethical")
    if re.search(r"\bhow might|what if|redesign|reimagin|alternative", t):
        labs.append("Transformational")
    if re.search(r"assumption|what are we not|frame|lens|\bmeta\b", t):
        labs.append("Meta")
    # dedupe order
    seen = set()
    return [x for x in labs if not (x in seen or seen.add(x))]


# ---- main ------------------------------------------------------------------

def compute_metrics(
    df: pd.DataFrame,
    label_col: str = "labels",
    text_col: str = "text",
    infer_if_missing: bool = True,
) -> Dict[str, float]:
    """
    Compute Spiral metrics from a DataFrame.

    Expects columns:
      - label_col: per-row labels (list, JSON string, or delimited string)
      - text_col:   used only if infer_if_missing=True and label parsing yields none

    Returns:
      dict with headline indices (SDI, EDS, TD, MAI) and per-layer coverage in [0,1].
    """
    if label_col not in df.columns and infer_if_missing and text_col not in df.columns:
        raise ValueError(f"Need '{label_col}' or (if inferring) '{text_col}' in DataFrame.")

    counts = Counter()
    total = 0

    for _, row in df.iterrows():
        labs = _norm_labels(row.get(label_col, ""))

        if not labs and infer_if_missing:
            labs = _infer_from_text(row.get(text_col, ""))

        for l in labs:
            if l in LAYERS:
                counts[l] += 1
                total += 1

    total = max(total, 1)  # avoid div/0

    coverage = {l: counts.get(l, 0) / total for l in LAYERS}

    # headline indices
    sdi = sum(1 for l in LAYERS if counts.get(l, 0) > 0) / len(LAYERS)  # Spiral Diversity Index
    eds = coverage["Ethical"]            # Ethical Depth Share
    td  = coverage["Transformational"]   # Transformational Density
    mai = coverage["Meta"]               # Meta Awareness Index

    return {"SDI": sdi, "EDS": eds, "TD": td, "MAI": mai, **coverage}
