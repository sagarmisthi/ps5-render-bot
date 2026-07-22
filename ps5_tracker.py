import time
import requests
import threading
import os
from bs4 import BeautifulSoup
from flask import Flask

# --- YOUR CREDENTIALS ---
TELEGRAM_BOT_TOKEN = "8732648482:AAHqU0b9EpZWvLTKaaWMpmjAPs2Db6cMFT8"
TELEGRAM_CHAT_ID = "7700368660" 
PINCODE = "110018"

PROXY_URL = "http://45.168.238.193:8443"

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

PRODUCT_URL = "https://www.flipkart.com/sony-playstation5-console-slim-cfi-2008a01x-cfi-2116a01y-1-tb/p/itm89489e2adcd2c?pid=GMCGZCYPAFYBUNAR"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

COOKIES = {
    "pincode": PINCODE
}

# --- FLASK WEB SERVER FOR UPTIMEROBOT ---
app = Flask(__name__)

@app.route('/')
def home():
    return "PS5 Bot is awake and running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIC ---
def send_telegram_alert(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(telegram_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def check_stock():
    print(f"Checking Flipkart stock through proxy {PROXY_URL}...")
    try:
        response = requests.get(
            PRODUCT_URL, 
            headers=HEADERS, 
            cookies=COOKIES, 
            proxies=PROXIES, 
            timeout=30
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text(separator=' ', strip=True).upper()
            
            is_buyable = "BUY NOW" in page_text or "ADD TO CART" in page_text
            is_in_stock = "CURRENTLY OUT OF STOCK" not in page_text
            is_deliverable = "NOT DELIVERABLE" not in page_text and "NO SELLER SHIPS" not in page_text
            
            if is_buyable and is_in_stock and is_deliverable:
                msg = f"🚨 PS5 IS IN STOCK FOR PINCODE {PINCODE}!\n\nBuy immediately:\n{PRODUCT_URL}"
                print("[!] Stock found! Sending alert...")
                send_telegram_alert(msg)
                return True
            else:
                print("Status: Out of stock or not deliverable.")
        else:
            print(f"HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"Proxy Connection error: {e}")
    return False

if __name__ == "__main__":
    # Start the dummy website in the background
    server_thread = threading.Thread(target=run_web_server)
    server_thread.start()
    
    print("Starting PS5 proxy tracker...")
    send_telegram_alert("✅ Cloud server is now monitoring Flipkart and ready for UptimeRobot!")
    
    while True:
        in_stock = check_stock()
        if in_stock:
            time.sleep(300) 
        else:
            time.sleep(45) 
