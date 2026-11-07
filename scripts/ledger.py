import json, re, os, datetime, sys

ROOT = r"C:\iran-war-test"
SYNTH = os.path.join(ROOT, "analyses", "10_revised_synthesis_round5.md")
LEDGER = os.path.join(ROOT, "predictions", "ledger.jsonl")

def extract(text):
    # Find the FINAL WAR PROBABILITY section
    final = re.search(r"FINAL WAR PROBABILITY(.+?)(?:UNCERTAINTY|TOP 3|$)", text, re.S)
    if not final:
        return "unknown", None, [], [], []
    section = final.group(1)

    # probability range: first XX-YY% inside the FINAL section
    m = re.search(r"(\d{2})\s*[-–]\s*(\d{2})%", section)
    prob = f"{m.group(1)}-{m.group(2)}%" if m else "unknown"

    # window start
    m = re.search(r"Window\*\*:?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
    win_start = m.group(1) if m else None

    # key evidence (from AGREEMENTS and DISAGREEMENTS anywhere in the file)
    agreements = re.findall(r"\*\*(\d+)\.\s*(.+?)\*\*", text)
    disagreements = re.findall(r"\*\*([A-I])\.\s*(.+?)\*\*", text)
    key_evidence = [a[1] for a in agreements] + [d[1] for d in disagreements]

    # threshold events: from TOP 3 THRESHOLD EVENTS section
    top = re.search(r"TOP 3 THRESHOLD EVENTS(.+?)(?:TOP 3 MISSING|$)", text, re.S)
    thresholds = []
    if top:
        for m in re.finditer(r"\*\*(\d)\.\s*(.+?)\*\*", top.group(1), re.S):
            thresholds.append(m.group(2).strip())

    # sources
    sources = sorted(set(re.findall(r"[\w\-]+\.md", text)))

    return prob, win_start, key_evidence, thresholds, sources

def main():
    if not os.path.exists(SYNTH):
        print("synthesis file not found:", SYNTH); sys.exit(1)
    text = open(SYNTH, encoding="utf-8").read()
    prob, win_start, key_evidence, thresholds, sources = extract(text)

    record = {
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "window_start": win_start,
        "probability_range": prob,
        "key_evidence": key_evidence[:10],
        "threshold_events": thresholds[:3],
        "sources_used": sources,
        "synthesis_file": os.path.relpath(SYNTH, ROOT),
    }

    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("appended record:", LEDGER)
    print("probability:", prob, "| evidence items:", len(key_evidence), "| thresholds:", len(thresholds), "| sources:", len(sources))

if __name__ == "__main__":
    main()