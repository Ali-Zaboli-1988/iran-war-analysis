import json, os, urllib.request, urllib.parse, datetime, sys

OUT = r"C:\iran-war-test\news_data\gdelt_iran.json"

# GDELT DOC 2.0 API: last 3 days, Iran-related, English + Persian
# Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
queries = [
    ("english", "Iran"),
    ("english", "Iran military"),
    ("english", "Strait of Hormuz"),
    ("persian", "ایران"),
]

def fetch(query, lang, days=3):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=days)
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": "250",
        "format": "json",
        "startdatetime": start.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end.strftime("%Y%m%d%H%M%S"),
    }
    if lang == "persian":
        params["sourcelang"] = "persian"
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("articles", [])
    except Exception as e:
        print(f"  fetch failed for '{query}': {e}", file=sys.stderr)
        return []

def main():
    all_items = []
    seen_urls = set()
    for lang, q in queries:
        print(f"fetching [{lang}] {q} ...")
        items = fetch(q, lang)
        for it in items:
            u = it.get("url")
            if not u or u in seen_urls:
                continue
            seen_urls.add(u)
            all_items.append({
                "query": q,
                "lang": lang,
                "title": it.get("title"),
                "url": u,
                "source": it.get("domain"),
                "seendate": it.get("seendate"),
                "language": it.get("language"),
                "sourcecountry": it.get("sourcecountry"),
            })
        print(f"  got {len(items)} items")

    result = {
        "generated_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "window_days": 3,
        "queries": [q for _, q in queries],
        "total_unique": len(all_items),
        "items": all_items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"saved {len(all_items)} unique items -> {OUT}")

if __name__ == "__main__":
    main()