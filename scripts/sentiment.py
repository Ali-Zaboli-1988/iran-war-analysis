import json, os, re, sys, datetime

ROOT = r"C:\iran-war-test"
NEWS_DIR = os.path.join(ROOT, "news_data")

FEAR = [
    "fear", "threat", "warn", "risk", "danger", "escalat", "imminent", "attack",
    "strike", "nuclear", "war", "crisis", "collapse", "alarm", "panic", "hostile",
    "تهدید", "ترس", "هشدار", "خطر", "تشدید", "قریب", "حمله", "ضربه",
    "هسته‌ای", "هسته ای", "جنگ", "بحران", "فروپاشی", "اضطراب", "وحشت",
    "نگرانی", "نگران", "احتمال", "ریسک", "تهاجم", "درگیری", "تنش",
    "ناامنی", "خطرناک", "تهدیدآمیز", "هولناک",
]
ANGER = [
    "anger", "rage", "retaliat", "revenge", "punish", "destroy", "eliminat",
    "crush", "defian", "vow", "hostile", "fury", "outrage", "threaten",
    "خشم", "انتقام", "انتقام‌گیری", "انتقامجویی", "تلافی", "مجازات",
    "نابودی", "حذف", "سرکوب", "توهین", "غضب", "خصمانه", "عصبان",
    "قاطع", "قاطعانه", "بی‌رحم", "شدید", "برخورد", "پاسخ کوبنده",
    "خط قرمز", "تحمیل", "مقابله به مثل",
]
HOPE = [
    "hope", "negotiat", "mediat", "ceasefire", "deal", "agreement",
    "diplomac", "talk", "compromise", "peace", "settle", "truce",
    "امید", "مذاکره", "میانجی", "میانجی‌گری", "آتش‌بس", "توافق", "دیپلماسی",
    "گفتگو", "سازش", "صلح", "تفاهم", "توافقنامه", "راه‌حل سیاسی",
    "تنش‌زدایی", "آرامش", "صلح‌آمیز", "مذاکرات", "میانجیگری",
]

def classify(text):
    t = text.lower()
    f = sum(1 for w in FEAR if w in t)
    a = sum(1 for w in ANGER if w in t)
    h = sum(1 for w in HOPE if w in t)
    return f, a, h

def split_items(text):
    blocks = re.split(r"(?m)^#{3,4} ", text)
    return [b for b in blocks[1:]]

def lang_of(block):
    fa = re.search(r"[\u0600-\u06FF]", block)
    return "fa" if fa else "en"

def main():
    digest = None
    candidates = [
        os.path.join(NEWS_DIR, f)
        for f in os.listdir(NEWS_DIR)
        if f.startswith("rss_iran_") and f.endswith(".md")
    ]
    if candidates:
        digest = max(candidates, key=os.path.getmtime)
    if not digest:
        print("no rss_iran_*.md digest found", file=sys.stderr)
        sys.exit(1)

    text = open(digest, encoding="utf-8", errors="replace").read()
    items = split_items(text)

    stats = {"en": {"fear": 0, "anger": 0, "hope": 0, "count": 0},
             "fa": {"fear": 0, "anger": 0, "hope": 0, "count": 0}}

    for it in items:
        lang = lang_of(it)
        f, a, h = classify(it)
        stats[lang]["fear"] += f
        stats[lang]["anger"] += a
        stats[lang]["hope"] += h
        stats[lang]["count"] += 1

    def ratio(s):
        return round(s["fear"] / s["anger"], 2) if s["anger"] else None

    out = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "digest": os.path.basename(digest),
        "total_items": len(items),
        "english": {
            "items": stats["en"]["count"],
            "fear": stats["en"]["fear"],
            "anger": stats["en"]["anger"],
            "hope": stats["en"]["hope"],
            "fear_to_anger": ratio(stats["en"]),
        },
        "persian": {
            "items": stats["fa"]["count"],
            "fear": stats["fa"]["fear"],
            "anger": stats["fa"]["anger"],
            "hope": stats["fa"]["hope"],
            "fear_to_anger": ratio(stats["fa"]),
        },
    }

    outpath = os.path.join(NEWS_DIR, "sentiment_" + datetime.date.today().isoformat() + ".json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()