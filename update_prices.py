import csv
import json
import re
import time
import urllib.parse
import urllib.request

CSV_FILE = "games.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


def query_pricecharting(title, console="playstation-3"):
    """Searches PriceCharting for the game and extracts current Loose, CIB, and New prices."""
    clean_title = re.sub(r"\(.*?\)", "", title).strip()
    query = urllib.parse.quote(f"{clean_title} {console}")
    url = f"https://www.pricecharting.com/search-products?type=videogames&q={query}"

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Fallback regex parser for PriceCharting price cells
        cib_match = re.search(r'class="price js-price"[^>]*data-price="(\d+)"', html)
        if cib_match:
            price_cents = float(cib_match.group(1))
            return round(price_cents / 100.0, 2)
    except Exception as e:
        print(f"Skipping {title}: {e}")

    return None


def main():
    rows = []
    with open(CSV_FILE, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            title = row.get("Title", "")
            print(f"Checking market price: {title}...")

            latest_cib = query_pricecharting(title)
            if latest_cib:
                row["Estimated_Value_CIB"] = f"{latest_cib:.2f}"
                row["Current_Estimated_Value"] = f"{latest_cib:.2f}"
                print(f"-> Updated CIB: €{latest_cib:.2f}")

            rows.append(row)
            time.sleep(1.5)  # Respect rate limits

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Daily price update complete.")


if __name__ == "__main__":
    main()
