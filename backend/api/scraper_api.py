from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from urllib.parse import quote
import time
import os

app = Flask(__name__)

def extract_suburb_postcode(address):
    parts = address.strip().split(',')
    if len(parts) < 2:
        return None, None
    suburb = parts[-2].strip().lower().replace(' ', '-')
    postcode = parts[-1].strip()
    return suburb, postcode

def scrape_inspections(suburb, postcode, date):
    print(f"Scraping inspection times for: {suburb} NSW {postcode} on {date}")

    options = FirefoxOptions()
    # Comment out headless mode to debug visually if needed
    options.add_argument("--headless")

    service = FirefoxService()
    driver = webdriver.Firefox(service=service, options=options)

    try:
        url = f"https://www.domain.com.au/sale/{suburb}-nsw-{postcode}/inspection-times/?inspectiondate={quote(date)}"
        print("Navigating to:", url)
        driver.get(url)

        time.sleep(10)  # Wait for JS to load

        # Screenshot for debug
        screenshot_path = os.path.join(os.getcwd(), "debug_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")

        listings = driver.find_elements(By.CSS_SELECTOR, "[data-testid='listing-card-wrapper-standard']")
        print(f"Found {len(listings)} listings on the page")

        inspections = []
        for listing in listings:
            try:
                address_elem = listing.find_element(By.CSS_SELECTOR, "[data-testid='address-label']")
                time_elem = listing.find_element(By.CSS_SELECTOR, "[data-testid='inspection-time']")
                time_text = time_elem.text.strip()

                if "–" not in time_text:
                    continue

                _, time_range = time_text.rsplit(' ', 1)
                start_time, end_time = time_range.split("–")

                inspections.append({
                    'address': address_elem.text.strip(),
                    'date': date,
                    'start_time': start_time.strip(),
                    'end_time': end_time.strip()
                })
            except Exception as e:
                print("Error in listing parse:", e)
                continue

        return inspections
    finally:
        driver.quit()

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
