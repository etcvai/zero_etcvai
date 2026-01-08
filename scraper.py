import requests
from bs4 import BeautifulSoup
import time
import sys

# Configuration
BASE_URL = "https://dflix.discoveryftp.net"
OUTPUT_FILE = "dflix_playlist.m3u"

# Headers are critical - we pretend to be a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
}

CATEGORIES = [
    ("Bangla", "category/Bangla"),
    ("English", "category/English"),
    ("Hindi", "category/Hindi"),
    ("South", "category/Tamil"), # "Tamil" in your Kotlin code, mapped to "South" often
    ("Animation", "category/Animation")
]

def get_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        print(f"Connecting to {BASE_URL}...")
        # 1. Hit the main page first to get initial cookies
        session.get(BASE_URL, timeout=15)
        
        # 2. Perform the specific login
        # Kotlin Source [4]: "https://dflix.discoveryftp.net/login/demo"
        print("Authenticating...")
        login_resp = session.get(f"{BASE_URL}/login/demo", timeout=15)
        
        if login_resp.status_code == 200:
            print("Login success.")
            return session
        else:
            print(f"Login returned status: {login_resp.status_code}")
            return session # Try anyway, sometimes cookies are set regardless
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def scrape_movies(session):
    playlist_entries = []
    
    for name, route in CATEGORIES:
        # Kotlin Source [5]: "$mainUrl/m/${request.data}/$page"
        list_url = f"{BASE_URL}/m/{route}/1" 
        print(f"Scanning: {name} ({list_url})")
        
        try:
            resp = session.get(list_url, timeout=15)
            # Check if we got redirected to login (soft block)
            if "login" in resp.url and "category" not in resp.url:
                print("  ! Redirected to login page. Session might be invalid.")
                continue

            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Select cards - Kotlin Source [5]: "div.card"
            cards = soup.select("div.card")
            print(f"  Found {len(cards)} items.")
            
            for card in cards:
                try:
                    # Robust extraction
                    link_el = card.find("a")
                    # Title is often in h3 inside the second div
                    title_el = card.select_one("h3") 
                    img_el = card.select_one("img")
                    
                    if link_el and title_el:
                        relative_link = link_el.get('href', '')
                        details_url = BASE_URL + relative_link if not relative_link.startswith('http') else relative_link
                        
                        title = title_el.get_text(strip=True)
                        poster = img_el.get('src', '') if img_el else ""
                        
                        # Go to details page - Kotlin Source [10]
                        # We need the 'dataUrl'
                        detail_resp = session.get(details_url, timeout=10)
                        detail_soup = BeautifulSoup(detail_resp.content, 'html.parser')
                        
                        # Kotlin Source [10]: select("div.col-md-12:nth-child(3) > div:nth-child(1) > a:nth-child(1)")
                        # We'll use a broader selector for the "Watch/Download" button usually found in main banner
                        video_btn = detail_soup.select_one(".movie-detail-content a[href*='/play/'], .movie-detail-content a[href*='/download/']")
                        
                        # Fallback to the Kotlin specific selector if generic fails
                        if not video_btn:
                             video_btn = detail_soup.select_one("div.col-md-12 a")

                        if video_btn:
                            stream_url = video_btn.get('href')
                            if stream_url:
                                entry = f'#EXTINF:-1 tvg-logo="{poster}" group-title="{name}",{title}\n{stream_url}'
                                playlist_entries.append(entry)
                                print(f"    + {title}")
                        
                        time.sleep(0.1) # Fast but polite
                except Exception as e:
                    print(f"    Error parsing movie: {e}")
                    continue
                    
        except Exception as e:
            print(f"  Failed to load category {name}: {e}")
            
    return playlist_entries

def main():
    session = get_session()
    entries = []
    
    if session:
        entries = scrape_movies(session)
    
    # CRITICAL FIX: Open file for writing OUTSIDE the 'if entries' check.
    # This ensures the file is created even if 0 items are found, preventing git crash.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if entries:
            f.write("\n".join(entries))
            print(f"SUCCESS: Saved {len(entries)} items to {OUTPUT_FILE}")
        else:
            f.write("# No items found. Check scraper logs.\n")
            print("WARNING: 0 items found. Created empty playlist.")

if __name__ == "__main__":
    main()
                        
