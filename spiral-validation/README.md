
# Spiral Validation (subfolder edition)

**Drop this whole `spiral-validation/` folder into your repo** (e.g. `shunyapublications.github.io/spiral-validation/`).  
Then launch the quick demo notebook on Binder:

```
https://mybinder.org/v2/gh/SHUNYARANBOOKS/SHUNYAPUBLICATIONS.GITHUB.IO/HEAD?labpath=spiral-validation%2Fnotebooks%2F00_quickstart.ipynb
```
> Replace `SHUNYARANBOOKS/SHUNYAPUBLICATIONS.GITHUB.IO` above with your actual repo owner/name if different.

## What it does
- Loads a tiny sample dialogue dataset (`data/sample_dialogues.csv`).
- Computes simple Spiral indices via `src/spiral_metrics.py`:
  - **SDI** (Spiral Diversity Index): breadth across the 5 layers.
  - **EDS**: Ethical presence, **TD**: Transformational presence, **MAI**: Meta presence.
- Plots a small bar chart of the indices.

## Local run
```
pip install pandas==2.2.2 numpy==1.26.4 matplotlib==3.8.4
jupyter lab  # or jupyter notebook
# open spiral-validation/notebooks/00_quickstart.ipynb
```
