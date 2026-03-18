import json
import argparse
import os
import requests
from bs4 import BeautifulSoup
import time

def load_config():
    config_path = 'config/teams.json'
    if not os.path.exists(config_path):
        print(f"❌ Error: Could not find {config_path}")
        return None
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("conferences", {})

def scrape_team(conference_id, team):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    team_slug = team["id"]
    url = team["roster_url"]
    
    # Save to the new output folder structure Claude set up
    folder_path = f"output/{conference_id}/{team_slug}"
    os.makedirs(folder_path, exist_ok=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"   ❌ Failed to connect to {team['name']}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        player_cards = soup.find_all('div', attrs={'data-test-id': 's-person-card-list__root'})
        
        roster_data = []
        for card in player_cards:
            player = {"name": "Unknown", "headshot_url": "", "position": "-", "year": "-", "jersey_number": "-"}
            
            # Name & Jersey
            for link in card.find_all('a'):
                text = link.text.strip().replace('\n', ' ').replace('\r', '')
                if text and "Full Bio" not in text:
                    if text.isdigit():
                        player["jersey_number"] = text
                    elif "Jersey" not in text:
                        player["name"] = text
                        
            # Headshot
            img_tag = card.find('img')
            if img_tag:
                img_url = img_tag.get('data-src') or img_tag.get('src', '')
                if img_url.startswith('/'):
                    img_url = url.split('/sports/')[0] + img_url
                player["headshot_url"] = img_url

            # Position & Year
            for span in card.find_all('span'):
                text = span.text.strip()
                if text in ['RHP', 'LHP', 'C', 'INF', 'OF', 'UTL', '1B', '2B', '3B', 'SS']:
                    player["position"] = text
                elif text in ['Fr.', 'So.', 'Jr.', 'Sr.', 'Gr.', 'RS Fr.', 'RS So.']:
                    player["year"] = text
                
            roster_data.append(player)
            
        # Save Roster
        with open(f"{folder_path}/roster.json", 'w', encoding='utf-8') as f:
            json.dump(roster_data, f, indent=4)
            
        print(f"   ✅ Saved {len(roster_data)} players for {team['name']}")
        
    except Exception as e:
        print(f"   ⚠️ Error scraping {team['name']}: {e}")

def run_scraper(target_conference):
    conferences = load_config()
    if not conferences: return

    if target_conference not in conferences:
        print(f"❌ Could not find conference: {target_conference}")
        return

    conf_data = conferences[target_conference]
    teams = conf_data.get("teams", [])
    
    print(f"\n🚀 Initiating PressBox Engine for {conf_data['name'].upper()}...")
    print("=" * 50)

    for team in teams:
        print(f"📡 Fetching {team['name']}...")
        scrape_team(target_conference, team)
        time.sleep(1) # Be nice to the servers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PressBox Master Scraper CLI")
    parser.add_argument('--scrape', type=str, help='Scrape a specific conference (e.g., sec, big-west)')
    
    args = parser.parse_args()

    if args.scrape:
        run_scraper(args.scrape.lower())
    else:
        print("Welcome to PressBox Core. Use 'python3 main.py --scrape big-west' to run.")
