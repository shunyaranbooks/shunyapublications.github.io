
from collections import Counter
import pandas as pd
import ast

LAYERS = ["Clarifying","Causal","Ethical","Transformational","Meta"]

def _norm_labels(val):
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        s = val.strip()
        if s.startswith("["):
            try:
                out = ast.literal_eval(s)
                if isinstance(out, list):
                    return out
            except Exception:
                pass
        return [s]
    return []

def compute_metrics(df: pd.DataFrame):
    """Expect columns: 'text', 'labels'
    Returns headline indices + per-layer coverage (0..1)."""
    counts = Counter()
    total = 0
    for _, row in df.iterrows():
        labs = _norm_labels(row.get('labels',''))
        for l in labs:
            if l in LAYERS:
                counts[l] += 1
                total += 1

    total = max(total, 1)
    coverage = {l: counts.get(l,0)/total for l in LAYERS}

    sdi = sum(1 for l in LAYERS if counts.get(l,0) > 0) / len(LAYERS)
    eds = coverage['Ethical']
    td  = coverage['Transformational']
    mai = coverage['Meta']

    return {'SDI': sdi, 'EDS': eds, 'TD': td, 'MAI': mai, **coverage}
