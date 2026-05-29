# ============================================================
# OFW FOREX TRACKER - FULL SCRAPER (ALL 6 BANKS)
# ============================================================
# Saves to 3 databases:
#   1. Local MySQL (your PC)
#   2. Aiven cloud
#   3. Filess.io cloud
#
# HOW TO USE:
#   1. Update all 3 DB configs below
#   2. Update .env file with both cloud passwords
#   3. Run: python ofw_step2_scraper.py
# ============================================================

import time
import os
import requests
import mysql.connector
from bs4              import BeautifulSoup
from datetime         import date
from dotenv           import load_dotenv
from selenium         import webdriver
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.common.by       import By
from selenium.webdriver.support.ui      import WebDriverWait
from selenium.webdriver.support         import expected_conditions as EC

# Load passwords from .env file
load_dotenv()
AIVEN_PASSWORD   = os.getenv("AIVEN_PASSWORD")
FILESS_PASSWORD  = os.getenv("FILESS_PASSWORD")


# ============================================================
# DATABASE CONFIGS
# ============================================================

# 1. Local MySQL
DB_LOCAL = {
    "host":     "localhost",
    "user":     "root",
    "password": "root1234",
    "database": "forex_db"
}

# 2. Aiven cloud
DB_AIVEN = {
    "host":     "mysql-2dfcc8e4-alsonlawrence-usd-to-php-tracker.c.aivencloud.com",
    "port":     14992,
    "user":     "avnadmin",
    "password": AIVEN_PASSWORD,
    "database": "defaultdb",
    "ssl_disabled": False
}

# 3. Filess.io cloud — update with your Filess details
DB_FILESS = {
    "host":     "r6ze70.h.filess.io",        # <-- update this
    "port":     61002,                       # <-- update if different
    "user":     "ofw_forex_db_popularten",    # <-- update this
    "password": FILESS_PASSWORD,
    "database": "ofw_forex_db_popularten"
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ============================================================
# SELENIUM SETUP
# ============================================================
def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")
    return webdriver.Chrome(options=options)


# ============================================================
# SCRAPERS
# ============================================================
def scrape_bpi():
    print("Scraping BPI...")
    try:
        response = requests.get(
            "https://www.bpi.com.ph/personal/bank/forex/rates",
            headers=HEADERS, timeout=10
        )
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            if "USD" in cells[0].get_text(strip=True).upper():
                buying  = float(cells[1].get_text(strip=True).replace(",", ""))
                selling = float(cells[2].get_text(strip=True).replace(",", ""))
                print(f"  ✓ BPI → Buying: {buying} | Selling: {selling}")
                return buying, selling
        print("  ✗ BPI: USD row not found")
        return None, None
    except Exception as e:
        print(f"  ✗ BPI failed: {e}")
        return None, None


def scrape_chinabank():
    print("Scraping China Bank...")
    try:
        response = requests.get(
            "https://www.chinabank.ph/forex-and-navpu",
            headers=HEADERS, timeout=10
        )
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            if "USD" in cells[0].get_text(strip=True).upper():
                buying  = float(cells[1].get_text(strip=True).replace(",", ""))
                selling = float(cells[2].get_text(strip=True).replace(",", ""))
                print(f"  ✓ China Bank → Buying: {buying} | Selling: {selling}")
                return buying, selling
        print("  ✗ China Bank: USD row not found")
        return None, None
    except Exception as e:
        print(f"  ✗ China Bank failed: {e}")
        return None, None


def scrape_bdo(driver):
    print("Scraping BDO...")
    try:
        driver.get("https://www.bdo.com.ph/forex")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            if "USD" in cells[0].get_text(strip=True).upper():
                buying  = float(cells[1].get_text(strip=True).replace(",", ""))
                selling = float(cells[2].get_text(strip=True).replace(",", ""))
                print(f"  ✓ BDO → Buying: {buying} | Selling: {selling}")
                return buying, selling
        print("  ✗ BDO: USD row not found")
        return None, None
    except Exception as e:
        print(f"  ✗ BDO failed: {e}")
        return None, None


def scrape_metrobank(driver):
    print("Scraping Metrobank...")
    try:
        driver.get("https://www.metrobank.com.ph/articles/forex")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            if "USD" in cells[0].get_text(strip=True).upper():
                buying  = float(cells[3].get_text(strip=True).replace(",", ""))
                selling = float(cells[4].get_text(strip=True).replace(",", ""))
                print(f"  ✓ Metrobank → Buying: {buying} | Selling: {selling}")
                return buying, selling
        print("  ✗ Metrobank: USD row not found")
        return None, None
    except Exception as e:
        print(f"  ✗ Metrobank failed: {e}")
        return None, None


def scrape_landbank(driver):
    print("Scraping LandBank...")
    try:
        driver.get("https://www.landbank.com/foreign-exchange-rate")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            if "USD" in cells[0].get_text(strip=True).upper():
                buying  = float(cells[1].get_text(strip=True).replace(",", ""))
                selling = float(cells[2].get_text(strip=True).replace(",", ""))
                print(f"  ✓ LandBank → Buying: {buying} | Selling: {selling}")
                return buying, selling
        print("  ✗ LandBank: USD row not found")
        return None, None
    except Exception as e:
        print(f"  ✗ LandBank failed: {e}")
        return None, None


def scrape_pnb(driver):
    print("Scraping PNB...")
    try:
        driver.get("https://www.pnb.com.ph/foreign-exchange-rate-135")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            if "USD" in cells[1].get_text(strip=True).upper():
                buying  = float(cells[2].get_text(strip=True).replace(",", ""))
                selling = float(cells[3].get_text(strip=True).replace(",", ""))
                print(f"  ✓ PNB → Buying: {buying} | Selling: {selling}")
                return buying, selling
        print("  ✗ PNB: USD row not found")
        return None, None
    except Exception as e:
        print(f"  ✗ PNB failed: {e}")
        return None, None


# ============================================================
# SAVE TO ONE DATABASE
# ============================================================
def save_to_db(config, bank_name, buying, selling):
    today      = date.today()
    connection = mysql.connector.connect(**config)
    cursor     = connection.cursor()

    cursor.execute(
        "SELECT id FROM ofw_bank_rates WHERE bank_name = %s AND date_recorded = %s",
        (bank_name, today)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            """UPDATE ofw_bank_rates
               SET usd_buying_rate = %s, usd_selling_rate = %s, scraped_at = NOW()
               WHERE bank_name = %s AND date_recorded = %s""",
            (buying, selling, bank_name, today)
        )
    else:
        cursor.execute(
            """INSERT INTO ofw_bank_rates
               (bank_name, usd_buying_rate, usd_selling_rate, date_recorded)
               VALUES (%s, %s, %s, %s)""",
            (bank_name, buying, selling, today)
        )

    connection.commit()
    cursor.close()
    connection.close()


# ============================================================
# SAVE TO ALL 3 DATABASES
# ============================================================
def save_rate(bank_name, buying, selling):
    if buying is None or selling is None:
        print(f"  Skipping {bank_name} — no rate found\n")
        return

    for label, config in [("Local", DB_LOCAL), ("Aiven", DB_AIVEN), ("Filess", DB_FILESS)]:
        try:
            save_to_db(config, bank_name, buying, selling)
            print(f"  ✓ Saved to {label}: {bank_name} → ₱{buying} / ₱{selling}")
        except Exception as e:
            print(f"  ✗ {label} save failed: {e}")

    print()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("OFW Forex Scraper — All 6 Banks → 3 Databases")
    print(f"Date: {date.today()}")
    print("=" * 55)

    b, s = scrape_bpi()
    save_rate("BPI", b, s)

    b, s = scrape_chinabank()
    save_rate("China Bank", b, s)

    print("Starting headless Chrome...")
    driver = create_driver()

    try:
        b, s = scrape_bdo(driver)
        save_rate("BDO", b, s)

        b, s = scrape_metrobank(driver)
        save_rate("Metrobank", b, s)

        b, s = scrape_landbank(driver)
        save_rate("LandBank", b, s)

        b, s = scrape_pnb(driver)
        save_rate("PNB", b, s)

    finally:
        driver.quit()
        print("Browser closed.")

    print("=" * 55)
    print("Done!")
    print("=" * 55)
