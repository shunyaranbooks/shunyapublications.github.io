# The Akhtar Reflector — Open Demo, Spec & Invitation (CC BY-SA 4.0)

Build and evaluate systems that sustain **recursive recognition**: modeling your model of them, over time and under noise.

- 🔬 **Benchmark**: Recognition Loop Test (RLT) with **Recursive Depth Score (RDS ≥ τ)**
- 🧩 **Modules**: valenced memory, attentional timing (intentional pause), behavioral adaptation, safety guards (mirror-to-glass, caps)
- 🧪 **Harness**: ablations, baselines, judge rubric, plots
- 🔐 **Ethics**: consent, IRB language, data governance

**Local demo (no keys):**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 7860
# open demo_ui/index.html in a browser (it talks to http://localhost:7860)
```

**License & Attribution**  
This kit (code, demo, spec, UI text) is released under **CC BY-SA 4.0**.  
Preferred attribution: “**The Akhtar Reflector — Open Demo, Spec & Invitation** by Shunya Publications (CC BY-SA 4.0).”  
**Excluded from CC BY-SA**: Logos/wordmarks and the book *The Akhtar Reflector* (all rights reserved).  
Book citation link: https://a.co/d/gSLNvzq
