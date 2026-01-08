import requests
from bs4 import BeautifulSoup
import time

# Configuration
BASE_URL = "https://dflix.discoveryftp.net"
OUTPUT_FILE = "dflix_playlist.m3u"

# Categories from your Kotlin code
CATEGORIES = [
    ("Bangla", "category/Bangla"),
    ("English", "category/English"),
    ("Hindi", "category/Hindi"),
    ("Tamil", "category/Tamil"),
    ("Animation", "category/Animation")
]

def get_session():
    """Mimics the login() function from Kotlin."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    try:
        # The provider uses /login/demo to get cookies
        print("Logging in...")
        session.get(f"{BASE_URL}/login/demo", timeout=15)
        return session
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def scrape_movies(session):
    playlist_entries = []
    
    for name, route in CATEGORIES:
        print(f"Scraping Category: {name}")
        # Scrape page 1 of each category
        list_url = f"{BASE_URL}/m/{route}/1" 
        
        try:
            resp = session.get(list_url, timeout=10)
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Select movie cards
            cards = soup.select("div.card")
            
            for card in cards:
                try:
                    # Logic from toResult()
                    link_tag = card.select_one("div.card > a:nth-child(1)")
                    title_tag = card.select_one("div.card > div:nth-child(2) > h3:nth-child(1)")
                    img_tag = card.select_one("div.poster > img:nth-child(1)")
                    
                    if link_tag and title_tag:
                        details_url = BASE_URL + link_tag['href']
                        title = title_tag.get_text(strip=True)
                        poster = img_tag['src'] if img_tag else ""
                        
                        # Go to details page to get the actual video link
                        # Logic from load()
                        details_resp = session.get(details_url, timeout=10)
                        details_soup = BeautifulSoup(details_resp.content, 'html.parser')
                        
                        # Extract the 'dataUrl' which is the video link
                        video_btn = details_soup.select_one("div.col-md-12:nth-child(3) > div:nth-child(1) > a:nth-child(1)")
                        
                        if video_btn:
                            stream_url = video_btn['href']
                            
                            # Create M3U Entry
                            entry = f'#EXTINF:-1 tvg-logo="{poster}" group-title="{name}",{title}\n{stream_url}'
                            playlist_entries.append(entry)
                            print(f"  Found: {title}")
                        
                        # Be polite to the server
                        time.sleep(0.5)

                except Exception as e:
                    print(f"  Error parsing card: {e}")
                    continue
                    
        except Exception as e:
            print(f"Failed to scrape category {name}: {e}")
            
    return playlist_entries

def main():
    session = get_session()
    if not session:
        return

    print("Starting scrape...")
    entries = scrape_movies(session)
    
    if entries:
        # Write to file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("\n".join(entries))
        print(f"Done! Saved {len(entries)} items to {OUTPUT_FILE}")
    else:
        print("No entries found or connection failed.")

if __name__ == "__main__":
    main()
    
