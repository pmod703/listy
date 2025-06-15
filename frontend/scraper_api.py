from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from urllib.parse import quote
import os
import csv
import subprocess

app = Flask(__name__)

def extract_suburb_postcode(address):
    parts = address.strip().split(',')
    if len(parts) < 2:
        return None, None
    suburb = parts[-2].strip().lower().replace(' ', '-')
    postcode = parts[-1].strip()
    return suburb, postcode

def scrape_inspections(suburb, postcode, date):
    results = []
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        url = f"https://www.domain.com.au/sale/{suburb}-nsw-{postcode}/inspection-times/?inspectiondate={quote(date)}"
        print(f"🔍 Navigating to: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(8000)

        page.screenshot(path="playwright_debug.png")
        print("📸 Screenshot saved as 'playwright_debug.png'")

        listings = page.locator("[data-testid='listing-card-wrapper-standard']")
        count = listings.count()
        print(f"📦 Found {count} listings")

        for i in range(count):
            try:
                item = listings.nth(i)

                address_loc = item.locator("[data-testid='address-label']")
                time_loc = item.locator("[data-testid='inspection-time']")

                if not address_loc.is_visible() or not time_loc.is_visible():
                    print(f"⏭ Skipping listing {i} — element not visible.")
                    continue

                address = address_loc.inner_text(timeout=2000)
                time_text = time_loc.inner_text(timeout=2000)

                if "–" not in time_text:
                    continue

                _, time_range = time_text.strip().rsplit(' ', 1)
                start, end = time_range.split("–")

                results.append({
                    "address": address.strip(),
                    "date": date,
                    "start_time": start.strip(),
                    "end_time": end.strip()
                })
            except Exception as e:
                print(f"⚠️ Skipped listing {i} due to error: {e}")
                continue

        browser.close()

    # ✅ Save to CSV on Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    csv_path = os.path.join(desktop_path, f"inspections_{suburb}_{date}.csv")

    with open(csv_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["address", "date", "start_time", "end_time"])
        writer.writeheader()
        writer.writerows(results)

    print(f"📁 CSV saved to: {csv_path}")
    print(f"📁 CSV absolute path: {os.path.abspath(csv_path)}")

    try:
        subprocess.run(["open", csv_path], check=True)
        print("📂 CSV opened in default app.")
    except Exception as e:
        print("⚠️ Failed to open CSV automatically:", e)

    return results

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    address = request.args.get('address')
    date = request.args.get('date')

    if not address or not date:
        return jsonify({'error': 'Missing address or date'}), 400

    suburb, postcode = extract_suburb_postcode(address)
    if not suburb or not postcode:
        return jsonify({'error': 'Invalid address format'}), 400

    try:
        results = scrape_inspections(suburb, postcode, date)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
