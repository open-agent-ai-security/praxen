# Threat-model Phase-0 probe (exploratory)

Working artifacts for the evidence-derived threat-model probe — see
`plans/DESIGN_THREAT_MODEL.md` (design) and
`plans/RESULTS_THREAT_MODEL_PROBE.md` (three rounds of results).

- `GRAPH_SPEC.md` — graph JSON spec (v0.3)
- `EXTRACT_PROMPT.md` — extraction-agent task prompt
- `render_probe.py` — deterministic lane-layout SVG renderer (`python3 render_probe.py <run>/graph.json <run>/threatmodel.html`)
- `compare_runs.py` — pair stability comparator (`python3 compare_runs.py <r1>/graph.json <r2>/graph.json`)
- `<slug>-r{1,2}/`, `v2/`, `v3/` — graph JSONs per round (v1 = spec 0.1/Fable 5; v2 = spec 0.2/Opus 5; v3 = spec 0.3/Opus 5, corrected remit semantics)
- `compare_*.txt` — recorded pair comparisons

Rendered HTML is generated output and untracked — re-render with
`render_probe.py`. Probe code is throwaway by design; the product design
lives in the plans documents.
