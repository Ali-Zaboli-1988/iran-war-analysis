import json, os, sys, datetime

ROOT = r"C:\iran-war-test"
LEDGER = os.path.join(ROOT, "predictions", "ledger.jsonl")
OUTCOMES = os.path.join(ROOT, "predictions", "outcomes.jsonl")
REPORT = os.path.join(ROOT, "predictions", "memory_report.md")

def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def parse_range(s):
    try:
        lo, hi = [int(x) for x in s.replace("%", "").split("-")]
        return lo, hi
    except Exception:
        return None, None

def main():
    ledger = load_jsonl(LEDGER)
    outcomes = load_jsonl(OUTCOMES)

    # index outcomes by ledger_index
    outcomes_by_idx = {}
    for o in outcomes:
        idx = o.get("ledger_index")
        if idx is not None:
            outcomes_by_idx.setdefault(idx, []).append(o)

    lines = []
    lines.append("# Memory Report — Prediction Ledger & Outcomes")
    lines.append("")
    lines.append(f"Generated: {datetime.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Ledger records: {len(ledger)}")
    lines.append(f"Outcome records: {len(outcomes)}")
    lines.append("")

    # 1. Range evolution
    lines.append("## 1. Range evolution")
    lines.append("")
    lines.append("| # | Created | Range | Midpoint | Synthesis file | Outcome | Brier |")
    lines.append("|---|---------|-------|----------|----------------|---------|-------|")
    briers = []
    for i, rec in enumerate(ledger):
        pr = rec.get("probability_range", "unknown")
        lo, hi = parse_range(pr)
        mid = f"{(lo+hi)/2:.1f}" if lo is not None else "—"
        outs = outcomes_by_idx.get(i, [])
        if outs:
            last = outs[-1]
            outcome = last.get("outcome", "—")
            brier = last.get("brier_score", "—")
            if isinstance(brier, (int, float)):
                briers.append(brier)
        else:
            outcome = "—"
            brier = "—"
        lines.append(f"| {i} | {rec.get('created_at','—')} | {pr} | {mid} | {rec.get('synthesis_file','—')} | {outcome} | {brier} |")
    lines.append("")

    # 2. Calibration
    lines.append("## 2. Calibration")
    lines.append("")
    if briers:
        avg = sum(briers) / len(briers)
        lines.append(f"- Evaluated predictions: {len(briers)}")
        lines.append(f"- Mean Brier score: {avg:.4f}")
        lines.append(f"- Best (lowest): {min(briers):.4f}")
        lines.append(f"- Worst (highest): {max(briers):.4f}")
        lines.append("")
        lines.append("Reference: 0 = perfect, 0.25 = coin-flip at 50%, 1 = worst.")
    else:
        lines.append("- No evaluated predictions yet. Run `scripts/backtest.py` after the window closes.")
    lines.append("")

    # 3. Range drift
    lines.append("## 3. Range drift")
    lines.append("")
    mids = []
    for rec in ledger:
        lo, hi = parse_range(rec.get("probability_range", ""))
        if lo is not None:
            mids.append((lo+hi)/2)
    if len(mids) >= 2:
        lines.append(f"- First midpoint: {mids[0]:.1f}")
        lines.append(f"- Latest midpoint: {mids[-1]:.1f}")
        lines.append(f"- Net drift: {mids[-1]-mids[0]:+.1f} points")
        lines.append("")
        if mids[-1] < mids[0]:
            lines.append("- Direction: the model has moved **down** over successive rounds.")
        elif mids[-1] > mids[0]:
            lines.append("- Direction: the model has moved **up** over successive rounds.")
        else:
            lines.append("- Direction: no net change.")
    else:
        lines.append("- Not enough records to compute drift.")
    lines.append("")

    # 4. Lessons
    lines.append("## 4. Lessons")
    lines.append("")
    lines.append("- Each new synthesis should read the previous `memory_report.md` before finalizing.")
    lines.append("- If the midpoint drifts more than 10 points without a new Gate firing, the judge must justify the drift explicitly.")
    lines.append("- If a Brier score exceeds 0.25 (coin-flip), the model was worse than random on that prediction; the corresponding synthesis should be re-read for systematic bias.")
    lines.append("")

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {REPORT}")
    print(f"ledger={len(ledger)} outcomes={len(outcomes)} evaluated={len(briers)}")

if __name__ == "__main__":
    main()