import os, re, glob, datetime, json

ROOT = r"C:\iran-war-test"
ANALYSES = os.path.join(ROOT, "analyses")
NEWS = os.path.join(ROOT, "news_data")
OUT_DIR = os.path.join(ROOT, "handoff")
OUT = os.path.join(OUT_DIR, "HANDOFF_session1.md")

def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""

def extract_block(text, header_regex):
    """Return the body of a section whose header matches header_regex,
    stopping at the next '## ' or ALL-CAPS line."""
    m = re.search(header_regex, text, re.M)
    if not m:
        return None
    start = m.end()
    rest = text[start:]
    nxt = re.search(r"(?m)^(?:## |[A-Z][A-Z0-9 ,\-–—]{3,}$)", rest)
    body = rest[:nxt.start()] if nxt else rest
    return body.strip()

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    now = datetime.datetime.now().isoformat(timespec="seconds")

    # file inventory
    inv = []
    for p in sorted(glob.glob(os.path.join(ANALYSES, "*.md"))):
        inv.append((os.path.basename(p), os.path.getsize(p)))

    # digest header (first 8 lines only — stats, not content)
    digest = None
    cands = glob.glob(os.path.join(NEWS, "rss_iran_*.md"))
    if cands:
        digest = max(cands, key=os.path.getmtime)
    digest_head = "\n".join(read(digest).splitlines()[:8]) if digest else "(no digest found)"

    s05 = read(os.path.join(ANALYSES, "05_final_synthesis.md"))
    s06 = read(os.path.join(ANALYSES, "06_skeptic_audit.md"))

    blocks = {
        "EVENT_DEFINED": extract_block(s05, r"^EVENT DEFINED\s*$"),
        "AGREEMENTS": extract_block(s05, r"^AGREEMENTS BETWEEN ANALYSTS\s*$"),
        "DISAGREEMENTS": extract_block(s05, r"^DISAGREEMENTS AND JUDGMENTS\s*$"),
        "UNCERTAINTY_WIDTH": extract_block(s05, r"^UNCERTAINTY WIDTH\s*$"),
        "SKEPTIC_CONTRADICTIONS": extract_block(s06, r"^CONTRADICTIONS\s*$"),
        "SKEPTIC_OVERALL": extract_block(s06, r"^OVERALL CHALLENGE STRENGTH\s*$"),
    }

    # insufficient information from each analyst
    insuff = {}
    for name in ["01_military.md", "02_economic.md", "03_political.md", "04_media.md"]:
        txt = read(os.path.join(ANALYSES, name))
        b = extract_block(txt, r"^INSUFFICIENT INFORMATION\s*$")
        if b:
            insuff[name] = b

    out = []
    out.append("# HANDOFF — Session 1 → Session 2")
    out.append("")
    out.append(f"Generated: {now}")
    out.append("")
    out.append("## 0. How to use this document")
    out.append("")
    out.append("This is an **extractive** handoff. Every block below is quoted from a file in `analyses/`.")
    out.append("No new judgment has been added. Session 2 must:")
    out.append("")
    out.append("1. Read this file first, as orientation.")
    out.append("2. Treat the quoted blocks as **session-1 decisions already made** — do not re-litigate them unless a *new* file provides new evidence.")
    out.append("3. Treat the skeptic contradictions as **unresolved** — session 2 may adjudicate them, but must not silently drop any.")
    out.append("4. **Not re-read the RSS digest.** Steps 5-9 do not require it.")
    out.append("5. **Not re-run Steps 1-4.** Their outputs are the files listed in §1.")
    out.append("6. If anything here conflicts with the actual files, the files win.")
    out.append("")
    out.append("## 1. File inventory (session-1 outputs)")
    out.append("")
    out.append("| File | Size (bytes) |")
    out.append("|---|---|")
    for n, s in inv:
        out.append(f"| `analyses/{n}` | {s} |")
    out.append("")
    out.append("## 2. Digest metadata (header only — do NOT re-read the body)")
    out.append("")
    out.append("```")
    out.append(digest_head)
    out.append("```")
    out.append("")
    out.append("## 3. Event definition already fixed in session 1 (from `05_final_synthesis.md`)")
    out.append("")
    out.append(blocks["EVENT_DEFINED"] or "(not found)")
    out.append("")
    out.append("## 4. Session-1 agreements (verbatim, from `05_final_synthesis.md`)")
    out.append("")
    out.append(blocks["AGREEMENTS"] or "(not found)")
    out.append("")
    out.append("## 5. Session-1 disagreements and judgments (verbatim, from `05_final_synthesis.md`)")
    out.append("")
    out.append(blocks["DISAGREEMENTS"] or "(not found)")
    out.append("")
    out.append("## 6. Skeptic contradictions (verbatim, from `06_skeptic_audit.md`)")
    out.append("")
    out.append(blocks["SKEPTIC_CONTRADICTIONS"] or "(not found)")
    out.append("")
    out.append("## 7. Skeptic overall challenge strength")
    out.append("")
    out.append(blocks["SKEPTIC_OVERALL"] or "(not found)")
    out.append("")
    out.append("## 8. Open questions per analyst (verbatim)")
    out.append("")
    for name, body in insuff.items():
        out.append(f"### {name}")
        out.append("")
        out.append(body)
        out.append("")
    out.append("## 9. Explicit non-goals for session 2")
    out.append("")
    out.append("- Do **not** redefine the event or the horizon.")
    out.append("- Do **not** re-open a contradiction that session 1 already resolved in §5, unless new evidence appears.")
    out.append("- Do **not** introduce facts not present in the files listed in §1.")
    out.append("- Do **not** claim a Decision Gate fired unless the files show its condition met.")
    out.append("")

    open(OUT, "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote {OUT} ({len(out)} lines)")
    print(f"blocks extracted: {sum(1 for v in blocks.values() if v)} / {len(blocks)}")
    print(f"analyst insufficient-info sections: {len(insuff)} / 4")

if __name__ == "__main__":
    main()