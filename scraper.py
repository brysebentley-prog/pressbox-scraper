import requests
from bs4 import BeautifulSoup
import json
import os

# 1. THE DICTIONARY: Add any D1 team here that uses Sidearm Sports!
TEAMS = {
    "big-west": {
        "cal-poly": "https://gopoly.com/sports/baseball/roster",
        "ucsb": "https://ucsbgauchos.com/sports/baseball/roster"
    }
}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

print("🚀 Starting PressBox Phase 2 Scraper...\n")

for conference, teams in TEAMS.items():
    for team, url in teams.items():
        print(f"📡 Fetching {team.upper()} ({conference})...")
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to connect to {team}. Skipping...\n")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        player_cards = soup.find_all('div', attrs={'data-test-id': 's-person-card-list__root'})
        
        roster_data = []
        
        for card in player_cards:
            player_info = {
                "name": "Unknown",
                "headshot_url": "No photo",
                "position": "N/A",
                "year": "N/A",
                "height": "N/A",
                "weight": "N/A",
                "hometown": "N/A"
            }
            
            # GET NAME
            links = card.find_all('a')
            for link in links:
                text = link.text.strip().replace('\n', ' ').replace('\r', '')
                if text and "Jersey" not in text and "Full Bio" not in text:
                    player_info["name"] = text
                    break 
                    
            # GET HEADSHOT
            img_tag = card.find('img')
            if img_tag:
                img_url = img_tag.get('data-src') or img_tag.get('src', 'No photo')
                if img_url.startswith('/'):
                    # Dynamically grab the base website (e.g., https://gopoly.com)
                    base_url = url.split('/sports/')[0]
                    img_url = base_url + img_url
                player_info["headshot_url"] = img_url
                
            # GET BIO STATS (Position, Height, Weight, Year, Hometown)
            # Sidearm usually puts these in a specific details container
            bio_section = card.find('div', class_='s-person-details__bio-stats')
            if bio_section:
                spans = bio_section.find_all('span')
                # Grab the text from each span, clean it up, and filter out empty ones
                bio_texts = [span.text.strip() for span in spans if span.text.strip()]
                
                if len(bio_texts) >= 1: player_info["position"] = bio_texts[0]
                if len(bio_texts) >= 2: player_info["year"] = bio_texts[1]
                if len(bio_texts) >= 3: player_info["height"] = bio_texts[2]
                if len(bio_texts) >= 4: player_info["weight"] = bio_texts[3]
            
            # GET HOMETOWN 
            hometown_section = card.find('div', class_='s-person-card__content__location')
            if hometown_section:
                player_info["hometown"] = hometown_section.text.strip().replace('\n', ' ')
                    
            roster_data.append(player_info)
            
        # 2. THE AUTO-FOLDERS: Create the directory structure safely
        folder_path = f"data/{conference}/{team}"
        os.makedirs(folder_path, exist_ok=True)
        
        # 3. SAVE THE FILE
        file_path = f"{folder_path}/roster.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(roster_data, f, indent=4)
            
        print(f"✅ Saved {len(roster_data)} players to {file_path}\n")

print("🏆 All scraping complete!")
