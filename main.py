import requests
import os

# The URL from your log
url = "https://akashgo.noobmaster.xyz/?api=iptv_m3u"

# Headers extracted from your request.json
headers = {
    "User-Agent": "okhttp/4.12.0",
    "Host": "akashgo.noobmaster.xyz",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip"
}

def fetch_playlist():
    try:
        print("Fetching playlist...")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Check if it's actually an M3U file
            content = response.text
            if "#EXTM3U" in content:
                # Save to a file named 'iptv.m3u'
                with open("iptv.m3u", "w", encoding="utf-8") as f:
                    f.write(content)
                print("✅ Success! Playlist saved to iptv.m3u")
            else:
                print("⚠️ Downloaded, but content doesn't look like M3U.")
                print(content[:100]) # Print first 100 chars to debug
        else:
            print(f"❌ Failed to fetch. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_playlist()
          
