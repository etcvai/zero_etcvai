import requests
import os

# ==========================================
# CONFIGURATION
# ==========================================
SOURCE_URL = "https://falconcastapp.info/playlist/ftp/app/playlist.m3u?id=160b2cfb48f9"

# Headers to trick the server (kept identical to your source)
HEADERS = {
    "User-Agent": "okhttp/4.12.0",
    "X-Requested-With": "com.faclconnew.live",
    "Accept-Encoding": "gzip",
    "Connection": "Keep-Alive",
    "Referer": "https://falconcastapp.info/"
}

def generate_playlist():
    print(f"[🔄] Fetching fresh playlist from server...")
    try:
        response = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            # Save the file
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"[✅] Playlist updated successfully!")
        else:
            print(f"[❌] Failed to fetch. Status: {response.status_code}")
            exit(1) # Exit with error to notify GitHub Actions
    except Exception as e:
        print(f"[❌] Error fetching playlist: {e}")
        exit(1)

if __name__ == "__main__":
    generate_playlist()
