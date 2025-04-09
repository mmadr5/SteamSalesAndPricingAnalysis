import requests
import json
import csv
import time
import os

url = 'https://api.gamalytic.com/publishers'
headers = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

all_publishers = []
page = 0
limit = 50

print("🔁 Starting publisher data retrieval...")

while True:
    params = {
        'fields': 'name,totalRevenue,averageRevenue,medianRevenue,class,inHouse,id,numberOfGames,genres',
        'limit': limit,
        'page': page
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error fetching page {page}: {e}")
        break

    publishers = data.get('result', [])

    if not publishers:
        print("✅ No more data. Finishing up...")
        break

    all_publishers.extend(publishers)
    print(f"📦 Page {page} — {len(publishers)} publishers collected (total: {len(all_publishers)})")

    # 🔐 Backup every 5 pages
    if page % 5 == 0:
        with open('gamalytic_publishers_backup.json', 'w', encoding='utf-8') as f:
            json.dump(all_publishers, f, ensure_ascii=False, indent=2)

    page += 1
    time.sleep(0.5)  # Polite delay

# ✅ Save full JSON
with open('gamalytic_publishers.json', 'w', encoding='utf-8') as f:
    json.dump(all_publishers, f, ensure_ascii=False, indent=4)

# ✅ Save to CSV
if all_publishers:
    fieldnames = list(all_publishers[0].keys())
    with open('gamalytic_publishers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_publishers)

    print(f"✅ All data saved! {len(all_publishers)} publishers written to:")
    print("  - gamalytic_publishers.json")
    print("  - gamalytic_publishers.csv")
else:
    print("⚠️ No publisher data to save.")
