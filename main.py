import requests
import json
import sys

# Source URL
JSON_URL = "https://psplay.indevs.in/icctv"
OUTPUT_FILE = "icc.m3u8"

def generate_playlist():
    try:
        print(f"Fetching data from {JSON_URL}...")
        response = requests.get(JSON_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            # Standard M3U header
            f.write('#EXTM3U x-tvg-url=""\n')

            channel_count = 0
            
            # 1. Loop through tournaments
            tournaments = data.get("tournaments", [])
            for tourney in tournaments:
                
                # 2. Loop through live_streams inside each tournament
                streams = tourney.get("live_streams", [])
                for stream in streams:
                    title = stream.get("title", "Unknown Match")
                    mpd_url = stream.get("mpd")
                    drm_keys = stream.get("keys")  # format "kid:key"
                    
                    # Extract logo from nested "match" object
                    match_info = stream.get("match", {})
                    logo = match_info.get("thumbnail", "")

                    if mpd_url:
                        # Write Metadata
                        f.write(f'#EXTINF:-1 tvg-id="{title}" tvg-name="{title}" tvg-logo="{logo}" group-title="ICC Live",{title}\n')
                        
                        # Write Kodi Props for DASH + ClearKey
                        f.write('#KODIPROP:inputstream.adaptive.manifest_type=mpd\n')
                        
                        if drm_keys:
                            f.write('#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n')
                            # The JSON "keys" format is already "kid:key", which matches Kodi requirements
                            f.write(f'#KODIPROP:inputstream.adaptive.license_key={drm_keys}\n')
                        
                        # Write the URL
                        f.write(f'{mpd_url}\n')
                        channel_count += 1

        print(f"Success: Generated {OUTPUT_FILE} with {channel_count} channels.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) # Exit with error code to notify GitHub Actions

if __name__ == "__main__":
    generate_playlist()
                headers = item.get("headers", "")
                user_agent = item.get("user_agent", "")
                
                # Construct Kodi-specific License tags if DRM is present in JSON
                # Example: #KODIPROP:inputstream.adaptive.license_key=...
                
                if link:
                    # Append user-agent to link for Kodi if needed (pipe syntax)
                    if user_agent and "|" not in link:
                        link = f"{link}|User-Agent={user_agent}"
                    
                    f.write(f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}" tvg-logo="{logo}" group-title="ICC Live",{name}\n')
                    f.write(f"{link}\n")
                    count += 1
        
        print(f"Success: Generated {OUTPUT_FILE} with {count} channels.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    generate_m3u8()
