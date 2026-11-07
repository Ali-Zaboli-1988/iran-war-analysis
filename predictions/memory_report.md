# Memory Report — Prediction Ledger & Outcomes

Generated: 2026-10-27T04:02:05
Ledger records: 6
Outcome records: 1

## 1. Range evolution

| # | Created | Range | Midpoint | Synthesis file | Outcome | Brier |
|---|---------|-------|----------|----------------|---------|-------|
| 0 | 2026-10-21T03:29:37 | 50-65% | 57.5 | analyses\05_final_synthesis.md | — | — |
| 1 | 2026-10-21T13:20:29 | 40-55% | 47.5 | analyses\07_revised_synthesis.md | — | — |
| 2 | 2026-10-21T14:50:19 | 40-55% | 47.5 | analyses\08_revised_synthesis_gated.md | no_war | 0.2256 |
| 3 | 2026-10-22T00:41:43 | 35-64% | 49.5 | analyses/10_revised_synthesis_round5.md | — | — |
| 4 | 2026-10-22T01:34:32 | 35-65% | 50.0 | analyses\10_revised_synthesis_round5.md | — | — |
| 5 | 2026-10-27T04:02:04 | 36-66% | 51.0 | analyses\10_revised_synthesis_round5.md | — | — |

## 2. Calibration

- Evaluated predictions: 1
- Mean Brier score: 0.2256
- Best (lowest): 0.2256
- Worst (highest): 0.2256

Reference: 0 = perfect, 0.25 = coin-flip at 50%, 1 = worst.

## 3. Range drift

- First midpoint: 57.5
- Latest midpoint: 51.0
- Net drift: -6.5 points

- Direction: the model has moved **down** over successive rounds.

## 4. Lessons

- Each new synthesis should read the previous `memory_report.md` before finalizing.
- If the midpoint drifts more than 10 points without a new Gate firing, the judge must justify the drift explicitly.
- If a Brier score exceeds 0.25 (coin-flip), the model was worse than random on that prediction; the corresponding synthesis should be re-read for systematic bias.
