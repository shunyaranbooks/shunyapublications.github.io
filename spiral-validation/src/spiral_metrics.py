# spiral-validation/src/spiral_metrics.py
# ------------------------------------------------------------
# Robust utilities to normalize labels, optionally infer layers
# from text, and compute Spiral metrics (SDI, EDS, TD, MAI).
# Works even when your CSV uses different column names or stores
# labels as strings like "['Clarifying']" or "Clarifying, Causal".
#
# Usage in a notebook:
#   from src.spiral_metrics import compute_metrics, diagnose_dataframe
#   metrics = compute_metrics(df)  # df has text/labels or synonyms
#   diagnose_dataframe(df)         # prints what was recognized
#
# CLI:
#   python -m src.spiral_metrics --csv data/sample_dialogues.csv
#   (optional) --label-col labels --text-col text --save-json outputs/metrics.json
# ------------------------------------------------------------

from __future__ import annotations

from collections import Counter
from typing import List, Dict, Optional, Tuple
import ast
import json
import re
import sys
import argparse

import pandas as pd


# ----- Canonical layers ------------------------------------------------------

LAYERS: List[str] = ["Clarifying", "Causal", "Ethical", "Transformational", "Meta"]
_CANON_DIRECT = {
    "clarifying": "Clarifying",
    "causal": "Causal",
    "ethical": "Ethical",
    "transformational": "Transformational",
    "meta": "Meta",
}

# Candidates for auto-detection of columns
LABEL_CANDIDATES = [
    "labels", "label", "layer", "layers",
    "category", "categories", "tag", "tags",
    "Label", "Layer", "Tags", "Categories",
]
TEXT_CANDIDATES = [
    "text", "question", "content", "utterance",
    "prompt", "message", "Text", "Question", "Content", "Message",
]


# ----- Helpers: canonize, normalize, infer ----------------------------------

_SPLIT_RE = re.compile(r"[;,|/]+|,\s*")

def _canonize(s: str) -> Optional[str]:
    """
    Map many spellings/phrases to a canonical layer name, else None.
    """
    if not s:
        return None
    k = s.strip().strip("'\"").lower()

    # direct matches
    if k in _CANON_DIRECT:
        return _CANON_DIRECT[k]

    # lenient synonyms / cues
    if k.startswith("clarif") or "what do we mean" in k or "define" in k or "example" in k:
        return "Clarifying"
    if k.startswith("cause") or k == "why" or "because" in k or "driver" in k:
        return "Causal"
    if k.startswith("ethic") or k.startswith("should") or "fair" in k or "harm" in k or "who benefits" in k:
        return "Ethical"
    if k.startswith("transform") or "reimagin" in k or "redesign" in k or "how might" in k or "what if" in k:
        return "Transformational"
    if k == "meta" or "assumption" in k or "what are we not" in k or "frame" in k or "lens" in k:
        return "Meta"
    return None


def _norm_labels(val) -> List[str]:
    """
    Accepts:
      - list like ['Clarifying']
      - JSON-ish string "['Clarifying']"
      - delimited string 'Clarifying, Causal'
    Returns canonical layer list with de-duplication.
    """
    # Gather raw tokens
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

    # Canonicalize and de-duplicate (order-preserving)
    seen = set()
    out: List[str] = []
    for token in raw:
        c = _canonize(token)
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _infer_from_text(text: str) -> List[str]:
    """
    Light heuristic inference of layers when labels are missing.
    """
    t = (text or "").lower()
    labs: List[str] = []
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
    # De-duplicate
    seen = set()
    return [x for x in labs if not (x in seen or seen.add(x))]


# ----- Normalization pipeline ------------------------------------------------

def detect_columns(
    df: pd.DataFrame,
    label_col: Optional[str] = None,
    text_col: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (label_col, text_col) after auto-detection if needed.
    """
    lc = label_col
    tc = text_col

    if lc is None:
        for c in LABEL_CANDIDATES:
            if c in df.columns:
                lc = c
                break

    if tc is None:
        for c in TEXT_CANDIDATES:
            if c in df.columns:
                tc = c
                break

    return lc, tc


def normalize_dataframe(
    df: pd.DataFrame,
    label_col: Optional[str] = None,
    text_col: Optional[str] = None,
    allow_infer: bool = True,
    keep_debug_cols: bool = True,
) -> pd.DataFrame:
    """
    Build a normalized 'labels_norm' column using:
      - canonicalization of provided labels
      - optional inference from text when missing
    Drops rows that still have no recognized label(s).
    """
    lc, tc = detect_columns(df, label_col, text_col)

    # Work on a shallow copy to avoid mutating caller's df
    out = df.copy()

    # Build labels_norm
    if lc and lc in out.columns:
        out["labels_norm"] = out[lc].apply(_norm_labels)
    else:
        out["labels_norm"] = [[] for _ in range(len(out))]

    # Inference if allowed and needed
    if allow_infer and tc and tc in out.columns:
        need = out["labels_norm"].map(len).eq(0)
        if need.any():
            out.loc[need, "labels_norm"] = out.loc[need, tc].apply(_infer_from_text)

    # Drop rows with no recognized label
    before = len(out)
    out = out[out["labels_norm"].map(len) > 0].reset_index(drop=True)
    after = len(out)

    if keep_debug_cols:
        out["_debug_rows_kept"] = f"{after}/{before}"
        out["_debug_label_col"] = lc or ""
        out["_debug_text_col"] = tc or ""

    return out


# ----- Metrics ---------------------------------------------------------------

def compute_metrics_from_counts(counts: Counter) -> Dict[str, float]:
    """
    Given a Counter of per-layer counts, return metric dict:
    SDI, EDS, TD, MAI plus per-layer coverage.
    """
    total = sum(counts.values()) or 1
    coverage = {l: counts.get(l, 0) / total for l in LAYERS}
    sdi = sum(1 for l in LAYERS if counts.get(l, 0) > 0) / len(LAYERS)
    eds = coverage["Ethical"]
    td = coverage["Transformational"]
    mai = coverage["Meta"]

    return {"SDI": sdi, "EDS": eds, "TD": td, "MAI": mai, **coverage}


def compute_metrics(
    df: pd.DataFrame,
    label_col: Optional[str] = None,
    text_col: Optional[str] = None,
    infer_if_missing: bool = True,
) -> Dict[str, float]:
    """
    High-level convenience:
      - auto-detect columns if not provided
      - normalize labels (and optionally infer from text)
      - compute headline metrics

    Returns dict with:
      SDI, EDS, TD, MAI and per-layer coverage (0..1).
    """
    ndf = normalize_dataframe(
        df,
        label_col=label_col,
        text_col=text_col,
        allow_infer=infer_if_missing,
        keep_debug_cols=False,
    )

    counts = Counter(l for labs in ndf["labels_norm"] for l in labs)
    return compute_metrics_from_counts(counts)


# ----- Diagnostics -----------------------------------------------------------

def diagnose_dataframe(
    df: pd.DataFrame,
    label_col: Optional[str] = None,
    text_col: Optional[str] = None,
    infer_if_missing: bool = True,
    print_samples: int = 5,
) -> Dict[str, float]:
    """
    Print detected columns, rows kept, per-layer counts, and metrics.
    Returns the metrics dict.
    """
    lc, tc = detect_columns(df, label_col, text_col)
    print("Detected label_col:", lc, "| text_col:", tc)

    ndf = normalize_dataframe(
        df,
        label_col=lc,
        text_col=tc,
        allow_infer=infer_if_missing,
        keep_debug_cols=True,
    )

    print("Rows kept after normalization/inference:", ndf["_debug_rows_kept"].iloc[0] if len(ndf) else "0/0")
    if len(ndf):
        print("Sample normalized rows:")
        print(ndf[[tc or "text", "labels_norm"]].head(print_samples))

    counts = Counter(l for labs in ndf["labels_norm"] for l in labs)
    print("Per-layer counts:", dict(counts))

    metrics = compute_metrics_from_counts(counts)
    print("METRICS:", metrics)
    return metrics


# ----- CLI ------------------------------------------------------------------

def _cli():
    p = argparse.ArgumentParser(description="Compute Spiral metrics from a CSV.")
    p.add_argument("--csv", required=True, help="Path to CSV file.")
    p.add_argument("--label-col", default=None, help="Label column name (optional).")
    p.add_argument("--text-col", default=None, help="Text column name (optional).")
    p.add_argument("--no-infer", action="store_true", help="Disable inference from text.")
    p.add_argument("--save-json", default=None, help="Path to save metrics JSON.")
    p.add_argument("--show", action="store_true", help="Print diagnostic details.")
    args = p.parse_args()

    df = pd.read_csv(args.csv)
    if args.show:
        metrics = diagnose_dataframe(
            df,
            label_col=args.label_col,
            text_col=args.text_col,
            infer_if_missing=(not args.no_infer),
        )
    else:
        metrics = compute_metrics(
            df,
            label_col=args.label_col,
            text_col=args.text_col,
            infer_if_missing=(not args.no_infer),
        )
        print(json.dumps(metrics, indent=2))

    if args.save_json:
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print("Saved:", args.save_json)


if __name__ == "__main__":
    # Allow running as: python -m src.spiral_metrics --csv data/sample_dialogues.csv --show
    _cli()
