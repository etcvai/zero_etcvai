import requests
import json
import sys

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
JSON_URL = "https://psplay.indevs.in/icctv/lol.php"
OUTPUT_FILE = "icc.m3u8"

# Default Promo Channel Details
PROMO_TITLE = "EXTENDERMAXTG"
PROMO_URL = "https://drive.google.com/uc?export=download&id=1CCtOaagdSgWN2KrZXP1Wll-KJHBlqqXE"
PROMO_LOGO = "https://i.ibb.co.com/7JsT97R6/a-sleek-professional-television-channel-k0s-Gqv-F4-Rfa-MPGG8x8-Ao-Bg-Nxp-WWef-BSL.jpg"

def generate_playlist():
    print(f"Fetching data from {JSON_URL}...")
    
    try:
        # Fetch JSON using default requests headers
        response = requests.get(JSON_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Network or JSON Error: {e}")
        sys.exit(1)

    m3u_content = ['#EXTM3U']
    
    # --- ADD DEFAULT PROMO CHANNEL START ---
    m3u_content.append(f'#EXTINF:-1 tvg-id="{PROMO_TITLE}" tvg-name="{PROMO_TITLE}" tvg-logo="{PROMO_LOGO}" group-title="PROMO",{PROMO_TITLE}')
    m3u_content.append(PROMO_URL)
    count = 1 
    # --- ADD DEFAULT PROMO CHANNEL END ---

    # Accessing live_streams from the root level of the JSON
    streams = data.get("live_streams", [])
    
    for stream in streams:
        title = stream.get("title", "Unknown Match")
        mpd_url = stream.get("manifest_Url")
        drm_keys = stream.get("keys")  # Format: "kid:key"
        
        match_info = stream.get("match", {})
        logo = match_info.get("thumbnail", "")

        if mpd_url:
            # 1. Metadata (ID, Logo, Group, Title)
            m3u_content.append(f'#EXTINF:-1 tvg-id="{title}" tvg-name="{title}" tvg-logo="{logo}" group-title="ICC Live",{title}')
            
            # 2. DRM & Stream Configuration
            m3u_content.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
            if drm_keys:
                m3u_content.append('#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey')
                m3u_content.append(f'#KODIPROP:inputstream.adaptive.license_key={drm_keys}')
            
            # 3. Stream URL
            m3u_content.append(mpd_url)
            count += 1

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
        print(f"Success: Generated {OUTPUT_FILE} with {count} channels (including Promo).")
    except Exception as e:
        print(f"File Write Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_playlist()
    
