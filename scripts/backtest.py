import json, os, sys, datetime

ROOT = r"C:\iran-war-test"
LEDGER = os.path.join(ROOT, "predictions", "ledger.jsonl")
OUTCOMES = os.path.join(ROOT, "predictions", "outcomes.jsonl")

def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    if len(sys.argv) < 3:
        print("Usage: python backtest.py <record_index> <outcome>")
        print("  record_index: 0-based index in ledger.jsonl (0 = first record)")
        print("  outcome: 'war' if full-scale war resumed within the window, 'no_war' otherwise")
        sys.exit(1)

    idx = int(sys.argv[1])
    outcome = sys.argv[2].lower()
    if outcome not in ("war", "no_war"):
        print("outcome must be 'war' or 'no_war'")
        sys.exit(1)

    records = load_jsonl(LEDGER)
    if idx < 0 or idx >= len(records):
        print(f"record index {idx} out of range (ledger has {len(records)} records)")
        sys.exit(1)

    rec = records[idx]
    prob_str = rec.get("probability_range", "")
    try:
        low, high = [int(x) for x in prob_str.replace("%", "").split("-")]
        mid = (low + high) / 2
    except Exception:
        print(f"could not parse probability_range: {prob_str!r}")
        sys.exit(1)

    # Brier score for a range: use midpoint as the point forecast
    # outcome = 1 if war, 0 if no war
    y = 1.0 if outcome == "war" else 0.0
    brier = (mid / 100.0 - y) ** 2

    record = {
        "evaluated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "ledger_index": idx,
        "created_at": rec.get("created_at"),
        "probability_range": prob_str,
        "midpoint": mid,
        "outcome": outcome,
        "brier_score": round(brier, 4),
        "synthesis_file": rec.get("synthesis_file"),
    }

    os.makedirs(os.path.dirname(OUTCOMES), exist_ok=True)
    with open(OUTCOMES, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("appended outcome:", OUTCOMES)
    print(f"record {idx}: range {prob_str}, midpoint {mid}%, outcome={outcome}, Brier={brier:.4f}")
    print("Note: Brier score 0 = perfect, 0.25 = coin-flip at 50%, 1 = worst.")

if __name__ == "__main__":
    main()