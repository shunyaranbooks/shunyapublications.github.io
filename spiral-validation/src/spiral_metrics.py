from typing import Dict
import pandas as pd
from .spiral_utils import layer_scores

def compute_metrics(df: pd.DataFrame) -> Dict[str, float]:
    layer_cols = ['clarifying','causal','ethical','transformational','meta']
    scored = df['text'].apply(layer_scores).apply(pd.Series)
    scored = scored[layer_cols]
    sdi = (scored.sum(axis=1) / len(layer_cols)).mean()
    eds = scored['ethical'].mean()
    td = scored['transformational'].var()
    mai = scored['meta'].mean()
    return {'SDI': float(sdi), 'EDS': float(eds), 'TD': float(td if pd.notna(td) else 0.0), 'MAI': float(mai)}
