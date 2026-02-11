import requests
import json
import sys

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
JSON_URL = "https://psplay.indevs.in/icctv/lol.php"
OUTPUT_FILE = "icc.m3u8"

# Headers mimicking a real browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REFERER = "https://www.icc-cricket.com/" 

def generate_playlist():
    print(f"Fetching data from {JSON_URL}...")
    
    try:
        response = requests.get(JSON_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Network or JSON Error: {e}")
        sys.exit(1)

    m3u_content = ['#EXTM3U']
    count = 0

    # The new JSON structure has 'live_streams' directly in the root
    streams = data.get("live_streams", [])
    
    for stream in streams:
        title = stream.get("title", "Unknown Match")
        # Updated key: manifest_Url instead of mpd
        mpd_url = stream.get("manifest_Url")
        drm_keys = stream.get("keys")  # "kid:key"
        
        match_info = stream.get("match", {})
        logo = match_info.get("thumbnail", "")

        if mpd_url:
            # 1. Metadata
            m3u_content.append(f'#EXTINF:-1 tvg-id="{title}" tvg-name="{title}" tvg-logo="{logo}" group-title="ICC Live",{title}')
            
            # 2. Player Headers (OTT Navigator / VLC)
            m3u_content.append(f'#EXTVLCOPT:http-user-agent={USER_AGENT}')
            m3u_content.append(f'#EXTVLCOPT:http-referrer={REFERER}')
            
            # 3. DRM Config (Kodi / Adaptive Plugins)
            m3u_content.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
            if drm_keys:
                m3u_content.append('#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey')
                m3u_content.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_keys}')
            
            # 4. Stream URL
            m3u_content.append(mpd_url)
            count += 1

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
        print(f"Success: Generated {OUTPUT_FILE} with {count} channels.")
    except Exception as e:
        print(f"File Write Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_playlist()
    
