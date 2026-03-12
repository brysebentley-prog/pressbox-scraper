import requests
from bs4 import BeautifulSoup
import json

url = "https://gopoly.com/sports/baseball/roster"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

print(f"Connecting to {url}...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ Connection successful! Extracting players...\n")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    player_cards = soup.find_all('div', attrs={'data-test-id': 's-person-card-list__root'})
    
    roster_data = []
    
    for card in player_cards:
        name = "Unknown Name"
        
        # 1. FIND THE NAME
        links = card.find_all('a')
        for link in links:
            text = link.text.strip().replace('\n', ' ').replace('\r', '')
            if text and "Jersey" not in text and "Full Bio" not in text:
                name = text
                break 
                
        # 2. FIND THE HEADSHOT
        img_url = "No photo found"
        img_tag = card.find('img')
        if img_tag:
            img_url = img_tag.get('data-src') or img_tag.get('src', 'No photo found')
            if img_url.startswith('/'):
                img_url = "https://gopoly.com" + img_url
                
        # 3. ADD TO OUR ROSTER LIST
        roster_data.append({
            "name": name,
            "headshot_url": img_url
        })
        
    print(f"🎉 Successfully scraped {len(roster_data)} players!")
    
    # --- NEW CODE: SAVE TO JSON ---
    with open('roster.json', 'w', encoding='utf-8') as f:
        json.dump(roster_data, f, indent=4)
    print("📁 Saved all data to roster.json in your current folder!")
    
else:
    print(f"❌ Failed to connect. Status code: {response.status_code}")

