# Iran War Risk Analysis System

A modular, multi-agent pipeline for collecting Iran-related news from 48+ RSS feeds, running four specialist analyses, subjecting the synthesis to an adversarial audit, applying explicit Decision Gates and an Uncertainty Width Model, cross-checking the result against prediction markets, and measuring fear/anger/hope in the discourse.

## Quick start

```powershell
cd C:\iran-war-test
opencode
# inside OpenCode:
@orchestrator Run the full pipeline.
```

## Pipeline steps

| Step | Agent/Skill | Output |
|------|-------------|--------|
| 1 | `read-rss-aggregator` skill | `news_data/rss_iran_<start>_<end>.md` |
| 2a | `@military-analyst` | `analyses/01_military.md` |
| 2b | `@economic-analyst` | `analyses/02_economic.md` |
| 2c | `@political-analyst` | `analyses/03_political.md` |
| 2d | `@media-analyst` | `analyses/04_media.md` |
| 4 | `@synthesis-judge` | `analyses/05_final_synthesis.md` |
| 4.5 | `@skeptic` | `analyses/06_skeptic_audit.md` |
| 4.6 | `@synthesis-judge` (revised) | `analyses/07_revised_synthesis.md` |
| 4.7 | `@synthesis-judge` (gated) | `analyses/08_revised_synthesis_gated.md` |
| 4.8 | `@synthesis-judge` (width model) | `analyses/10_revised_synthesis_round5.md` |
| 5 | `scripts/ledger.py` | `predictions/ledger.jsonl` |

## Directory layout

```
iran-war-test/
├── .opencode/
│   └── agents/              # agent definitions
│       ├── orchestrator.md
│       ├── military-analyst.md
│       ├── economic-analyst.md
│       ├── political-analyst.md
│       ├── media-analyst.md
│       ├── synthesis-judge.md
│       ├── skeptic.md
│       └── news-collector.md   (legacy, unused)
├── analyses/                # outputs of each pipeline step
├── news_data/               # current digest + polymarket JSON + sentiment JSON
├── news_data_archive/       # old news files (not read by analysts)
├── predictions/             # ledger.jsonl + outcomes.jsonl
├── references/              # feeds.opml copy (for skill cwd)
├── scripts/
│   ├── ledger.py            # appends a prediction record
│   ├── backtest.py          # records outcome + Brier score
│   ├── memory.py            # produces memory_report.md from ledger + outcomes
│   ├── polymarket_fetch.py  # fetches Polymarket Iran markets
│   ├── sentiment.py         # fear/anger/hope ratio per language
│   └── gdelt_fetch.py       # (deprecated — GDELT rate-limits aggressively)
├── README.md
└── AGENTS.md                # (optional) agent notes
```

## Dependencies

- **OpenCode** 1.19.3+ (CLI or Desktop)
- **Python** 3.11+
- **uv** (for the RSS skill) — `C:\Users\<user>\.local\bin\uv.exe`
- **feedparser** — installed automatically by `uv run --with feedparser`

## The RSS skill

The read-rss-aggregator skill is installed at:
- `C:\Users\<user>\.config\opencode\skills\read-rss-aggregator\`
- `C:\Users\<user>\.agents\skills\read-rss-aggregator\`

Both copies must have the same `references/feeds.opml` (~30 feeds). The skill is invoked as a **Skill**, not as an `@agent`.

## Design principles

1. **One dataset, many readers.** All four analysts read the same digest. This is a known limitation — their "agreement" is not independent confirmation. The `@skeptic` step exists precisely to compensate.
2. **Adversarial audit before final output.** The first synthesis (05) is always audited (06), and the revised synthesis (07) must address every contradiction.
3. **Decision Gates and Uncertainty Width Model.** The judge applies seven explicit Decision Gates (each with a FIRED / PARTIAL / NOT FIRED / INSUFFICIENT DATA status) and computes the range width from contradiction load, data gaps, source monoculture, and Gate-7 opacity. The width is computed, not asserted.
4. **Every run is logged.** `scripts/ledger.py` appends a JSON record to `predictions/ledger.jsonl`. Over time, this becomes a calibration dataset.
5. **External cross-checks.** Polymarket prices are fetched into `news_data/polymarket_iran.json` and reconciled in section "Cross-check with Polymarket" of the revised synthesis.
6. **Sentiment as a weak signal.** `scripts/sentiment.py` computes fear/anger/hope counts and the fear-to-anger ratio per language. It is descriptive, not predictive — a ratio of ~7.5 means the discourse is fear-dominated, not anger-dominated.
7. **No hidden dependencies.** Everything runs from the project directory. `news_data_archive/` is never read.

## What this system does NOT do

-  It does not fetch full article bodies. RSS gives headlines + 1-3 line summaries only.
-  It does not verify facts independently. It compares sources, not truth.
-  It does not learn from past predictions automatically. `ledger.jsonl` must be reviewed manually.
-  It does not model second-order effects (e.g., how a strike would change oil markets).

## Known issues

- **GDELT API** returns HTTP 429 aggressively. `scripts/gdelt_fetch.py` is kept for reference but is not used.
- **Wire replication** inflates apparent cross-corroboration. "12 outlets confirmed" often means 3 originals + 9 reprints.
- **The `news-collector` agent** is legacy. The pipeline uses the RSS skill instead.
- **Persian text** in the digest can produce mojibake in some terminals. Use `python -X utf8` consistently.

## Sentiment

```powershell
python -X utf8 "C:\iran-war-test\scripts\sentiment.py"
```

Outputs `news_data/sentiment_<date>.json` with fear/anger/hope counts and the fear-to-anger ratio, split by language (English vs Persian).

## Backtest
After the 90-day window closes (or earlier, if a Decision Gate fires), record the outcome:

```powershell
python -X utf8 "C:\iran-war-test\scripts\backtest.py" <ledger_index> war|no_war
```

Results are appended to `predictions/outcomes.jsonl` with a Brier score (0 = perfect, 0.25 = coin-flip at 50%, 1 = worst).

## Memory

```powershell
python -X utf8 "C:\iran-war-test\scripts\memory.py"
```


Produces predictions/memory_report.md with:

- range evolution across runs (midpoint drift),

- Brier calibration summary (once outcomes are recorded),

- three standing lessons: read the previous report before synthesizing, justify any >10-point drift without a Gate, and re-read any synthesis whose Brier exceeded 0.25.

## Calibration roadmap (future work)

1. Fill `predictions/ledger.jsonl` with 10+ runs.
2. After each run's window closes, record the outcome (war resumed yes/no).
3. Compute Brier score and calibration curve.
4. Only then adjust the model's stated confidence.

## License / attribution

Internal research prototype. Not for operational use without human review.

