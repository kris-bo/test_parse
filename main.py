import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# === Config ===
CHECK_INTERVAL = 60  # seconds (adjust as needed)
VIP_THRESHOLD = 4

# === Secrets from environment variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TICKETMASTER_URL = os.getenv("TICKETMASTER_URL")

def send_telegram_alert(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[X] Failed to send Telegram alert: {e}")

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # new headless mode, works better
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # SeleniumManager auto-downloads the driver and uses the right binary
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def check_for_vip():
    print("[*] Checking ticket page...")
    driver = None
    try:
        driver = get_driver()
        driver.get(TICKETMASTER_URL)
        time.sleep(20)  # wait for full page JS load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        vip_count = str(soup).count("VIP 1")
        print(f"[+] Found {vip_count} VIP 1 tickets.")

        if vip_count > VIP_THRESHOLD:
            print("[!!] VIP 1 tickets detected — sending alert!")
            send_telegram_alert(BOT_TOKEN, CHAT_ID, f"🎟️ VIP 1 tickets found! Count: {vip_count}\n{TICKETMASTER_URL}")
            return True

        print("[ ] No VIP 1 tickets found.")
    except Exception as e:
        print(f"[X] Error during Selenium run: {e}")
    finally:
        if driver:
            driver.quit()
    return False

if __name__ == "__main__":
    while True:
        if check_for_vip():
            break  # stop on success
        time.sleep(CHECK_INTERVAL)
