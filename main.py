import cloudscraper
import os

# 1. Target URL
url = "http://172.19.178.180/playlists1/?download=m3u_playlist"

# 2. Exact Headers from your logs
# We use the 'okhttp' User-Agent and the 'Sportzfy' package name
headers = {
    "Host": "172.19.178.80",
    "User-Agent": "okhttp/4.12.0",
    "X-Requested-With": "com.falconnew.live",
    "Accept-Encoding": "gzip"
}

def fetch_playlist():
    try:
        print("1. Initializing Cloudscraper...")
        # create_scraper tries to mimic a real browser to bypass Cloudflare
        scraper = cloudscraper.create_scraper() 

        print("2. Requesting playlist...")
        response = scraper.get(url, headers=headers)
        
        print(f"3. Server Status: {response.status_code}")

        if response.status_code == 200:
            content = response.text
            if "#EXTM3U" in content:
                with open("iptv.m3u", "w", encoding="utf-8") as f:
                    f.write(content)
                print("✅ Success! Playlist saved to iptv.m3u")
            else:
                print("⚠️ Server sent 200 OK, but content is not M3U.")
                print("Preview:", content[:100])
        else:
            print(f"❌ Failed. Code: {response.status_code}")
            print("Response:", response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_playlist()
        
