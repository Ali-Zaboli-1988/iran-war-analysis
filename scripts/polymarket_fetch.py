import json
import urllib.request
import urllib.parse

# جستجوی بازارهای مربوط به ایران
query = "Iran"
url = f"https://gamma-api.polymarket.com/public-search?q={urllib.parse.quote(query)}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    # نمایش نتایج
    if isinstance(data, dict) and 'events' in data:
        for event in data['events'][:5]:
            print(f"Event: {event.get('title')}")
            for market in event.get('markets', []):
                prices = market.get('outcomePrices')
                if prices:
                    # قیمت‌ها به صورت رشته JSON دوبل کدگذاری شده‌اند
                    price_list = json.loads(prices)
                    print(f"  - {market.get('question')}: {price_list}")
    else:
        print("Response structure:", data)
except Exception as e:
    print(f"Error: {e}")