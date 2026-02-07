import requests
import json
import sys

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
JSON_URL = "https://psplay.indevs.in/icctv"
OUTPUT_FILE = "icc.m3u8"

# Headers to make the player look like a real browser
# This fixes the "ENOENT" / 10-second stop issue
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REFERER = "https://www.icc-cricket.com/" 
ORIGIN = "https://www.icc-cricket.com"

def generate_playlist():
    print(f"Fetching data from {JSON_URL}...")
    
    try:
        # Use headers even when fetching the JSON to be safe
        req_headers = {"User-Agent": USER_AGENT}
        response = requests.get(JSON_URL, headers=req_headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Network or JSON Error: {e}")
        sys.exit(1)

    m3u_content = ['#EXTM3U x-tvg-url=""']
    count = 0

    tournaments = data.get("tournaments", [])
    
    if not tournaments:
        print("No tournaments found.")
    
    for tourney in tournaments:
        streams = tourney.get("live_streams", [])
        
        for stream in streams:
            title = stream.get("title", "Unknown Match")
            mpd_url = stream.get("mpd")
            drm_keys = stream.get("keys")
            
            match_info = stream.get("match", {})
            logo = match_info.get("thumbnail", "")

            if mpd_url:
                # -------------------------------------------------
                # THE FIX: Append Headers to the URL for Kodi/VLC
                # -------------------------------------------------
                # Kodi uses the pipe (|) syntax to attach headers to the request
                final_url = f"{mpd_url}|User-Agent={USER_AGENT}&Referer={REFERER}&Origin={ORIGIN}"

                # 1. Metadata
                m3u_content.append(f'#EXTINF:-1 tvg-id="{title}" tvg-name="{title}" tvg-logo="{logo}" group-title="ICC Live",{title}')
                
                # 2. DRM Props (ClearKey)
                m3u_content.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
                
                if drm_keys:
                    m3u_content.append('#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey')
                    # Note: We ensure the keys are raw. Sometimes keys need encoding, 
                    # but for this source "kid:key" usually works as is.
                    m3u_content.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_keys}')
                
                # 3. The URL with Headers
                m3u_content.append(final_url)
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
                    
