#!/usr/bin/env python3
"""
PressBox Team Discovery — ALL D1 Baseball Programs
Generates teams.json config with ~300 D1 baseball programs across all conferences.

Usage:
    python3 discover_teams.py                    # Add all conferences
    python3 discover_teams.py --list             # List all teams
    python3 discover_teams.py --conference sec    # Add only one conference
    python3 discover_teams.py --verify           # Verify URLs work
"""

import json
import os
import sys
import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def t(name, mascot, abbr, domain, c1, c2="#FFFFFF", city="", state=""):
    """Shorthand helper to create a team entry."""
    return {"name": name, "mascot": mascot, "abbr": abbr, "domain": domain, "colors": [c1, c2], "city": city, "state": state}

ALL_CONFERENCES = {

    # ====================== POWER CONFERENCES ======================

    "acc": {"name": "Atlantic Coast Conference", "teams": [
        t("Boston College", "Eagles", "BC", "bceagles.com", "#98002E", "#B3A369", "Chestnut Hill", "MA"),
        t("Clemson", "Tigers", "CLEM", "clemsontigers.com", "#F56600", "#522D80", "Clemson", "SC"),
        t("Duke", "Blue Devils", "DUKE", "goduke.com", "#003087", "#FFFFFF", "Durham", "NC"),
        t("Florida State", "Seminoles", "FSU", "seminoles.com", "#782F40", "#CEB888", "Tallahassee", "FL"),
        t("Georgia Tech", "Yellow Jackets", "GT", "ramblinwreck.com", "#B3A369", "#003057", "Atlanta", "GA"),
        t("Louisville", "Cardinals", "LOU", "gocards.com", "#AD0000", "#000000", "Louisville", "KY"),
        t("Miami", "Hurricanes", "MIA", "miamihurricanes.com", "#F47321", "#005030", "Coral Gables", "FL"),
        t("North Carolina", "Tar Heels", "UNC", "goheels.com", "#7BAFD4", "#13294B", "Chapel Hill", "NC"),
        t("NC State", "Wolfpack", "NCST", "gopack.com", "#CC0000", "#000000", "Raleigh", "NC"),
        t("Notre Dame", "Fighting Irish", "ND", "und.com", "#0C2340", "#C99700", "Notre Dame", "IN"),
        t("Pittsburgh", "Panthers", "PITT", "pittsburghpanthers.com", "#003594", "#FFB81C", "Pittsburgh", "PA"),
        t("SMU", "Mustangs", "SMU", "smumustangs.com", "#0033A0", "#C8102E", "Dallas", "TX"),
        t("Stanford", "Cardinal", "STAN", "gostanford.com", "#8C1515", "#FFFFFF", "Stanford", "CA"),
        t("Syracuse", "Orange", "SYR", "cuse.com", "#F76900", "#002244", "Syracuse", "NY"),
        t("Virginia", "Cavaliers", "UVA", "virginiasports.com", "#232D4B", "#F84C1E", "Charlottesville", "VA"),
        t("Virginia Tech", "Hokies", "VT", "hokiesports.com", "#630031", "#CF4420", "Blacksburg", "VA"),
        t("Wake Forest", "Demon Deacons", "WAKE", "godeacs.com", "#9E7E38", "#000000", "Winston-Salem", "NC"),
    ]},

    "sec": {"name": "Southeastern Conference", "teams": [
        t("Alabama", "Crimson Tide", "BAMA", "rolltide.com", "#9E1B32", "#FFFFFF", "Tuscaloosa", "AL"),
        t("Arkansas", "Razorbacks", "ARK", "arkansasrazorbacks.com", "#9D2235", "#FFFFFF", "Fayetteville", "AR"),
        t("Auburn", "Tigers", "AUB", "auburntigers.com", "#0C2340", "#E87722", "Auburn", "AL"),
        t("Florida", "Gators", "FLA", "floridagators.com", "#0021A5", "#FA4616", "Gainesville", "FL"),
        t("Georgia", "Bulldogs", "UGA", "georgiadogs.com", "#BA0C2F", "#000000", "Athens", "GA"),
        t("Kentucky", "Wildcats", "UK", "ukathletics.com", "#0033A0", "#FFFFFF", "Lexington", "KY"),
        t("LSU", "Tigers", "LSU", "lsusports.net", "#461D7C", "#FDD023", "Baton Rouge", "LA"),
        t("Mississippi State", "Bulldogs", "MSST", "hailstate.com", "#660000", "#FFFFFF", "Starkville", "MS"),
        t("Missouri", "Tigers", "MIZ", "mutigers.com", "#F1B82D", "#000000", "Columbia", "MO"),
        t("Oklahoma", "Sooners", "OU", "soonersports.com", "#841617", "#FDF9D8", "Norman", "OK"),
        t("Ole Miss", "Rebels", "MISS", "olemisssports.com", "#CE1126", "#14213D", "Oxford", "MS"),
        t("South Carolina", "Gamecocks", "SC", "gamecocksonline.com", "#73000A", "#000000", "Columbia", "SC"),
        t("Tennessee", "Volunteers", "TENN", "utsports.com", "#FF8200", "#FFFFFF", "Knoxville", "TN"),
        t("Texas", "Longhorns", "TEX", "texassports.com", "#BF5700", "#FFFFFF", "Austin", "TX"),
        t("Texas A&M", "Aggies", "TAMU", "12thman.com", "#500000", "#FFFFFF", "College Station", "TX"),
        t("Vanderbilt", "Commodores", "VANDY", "vucommodores.com", "#000000", "#866D4B", "Nashville", "TN"),
    ]},

    "big-12": {"name": "Big 12 Conference", "teams": [
        t("Arizona", "Wildcats", "ARIZ", "arizonawildcats.com", "#CC0033", "#003366", "Tucson", "AZ"),
        t("Arizona State", "Sun Devils", "ASU", "thesundevils.com", "#8C1D40", "#FFC627", "Tempe", "AZ"),
        t("BYU", "Cougars", "BYU", "byucougars.com", "#002E5D", "#FFFFFF", "Provo", "UT"),
        t("Baylor", "Bears", "BAY", "baylorbears.com", "#003015", "#FFB81C", "Waco", "TX"),
        t("Cincinnati", "Bearcats", "CIN", "gobearcats.com", "#E00122", "#000000", "Cincinnati", "OH"),
        t("Houston", "Cougars", "HOU", "uhcougars.com", "#C8102E", "#FFFFFF", "Houston", "TX"),
        t("Kansas", "Jayhawks", "KU", "kuathletics.com", "#0051BA", "#E8000D", "Lawrence", "KS"),
        t("Kansas State", "Wildcats", "KSU", "kstatesports.com", "#512888", "#FFFFFF", "Manhattan", "KS"),
        t("Oklahoma State", "Cowboys", "OKST", "okstate.com", "#FF7300", "#000000", "Stillwater", "OK"),
        t("TCU", "Horned Frogs", "TCU", "gofrogs.com", "#4D1979", "#FFFFFF", "Fort Worth", "TX"),
        t("Texas Tech", "Red Raiders", "TTU", "texastech.com", "#CC0000", "#000000", "Lubbock", "TX"),
        t("UCF", "Knights", "UCF", "ucfknights.com", "#000000", "#B4975A", "Orlando", "FL"),
        t("Utah", "Utes", "UTAH", "utahutes.com", "#CC0000", "#FFFFFF", "Salt Lake City", "UT"),
        t("West Virginia", "Mountaineers", "WVU", "wvusports.com", "#002855", "#EAAA00", "Morgantown", "WV"),
    ]},

    "big-ten": {"name": "Big Ten Conference", "teams": [
        t("Illinois", "Fighting Illini", "ILL", "fightingillini.com", "#E84A27", "#13294B", "Champaign", "IL"),
        t("Indiana", "Hoosiers", "IND", "iuhoosiers.com", "#990000", "#FFFFFF", "Bloomington", "IN"),
        t("Iowa", "Hawkeyes", "IOWA", "hawkeyesports.com", "#FFCD00", "#000000", "Iowa City", "IA"),
        t("Maryland", "Terrapins", "MD", "umterps.com", "#E03A3E", "#FFD200", "College Park", "MD"),
        t("Michigan", "Wolverines", "MICH", "mgoblue.com", "#00274C", "#FFCB05", "Ann Arbor", "MI"),
        t("Michigan State", "Spartans", "MSU", "msuspartans.com", "#18453B", "#FFFFFF", "East Lansing", "MI"),
        t("Minnesota", "Golden Gophers", "MINN", "gophersports.com", "#7A0019", "#FFCC33", "Minneapolis", "MN"),
        t("Nebraska", "Cornhuskers", "NEB", "huskers.com", "#E41C38", "#FFFFFF", "Lincoln", "NE"),
        t("Northwestern", "Wildcats", "NW", "nusports.com", "#4E2A84", "#FFFFFF", "Evanston", "IL"),
        t("Ohio State", "Buckeyes", "OSU", "ohiostatebuckeyes.com", "#BB0000", "#666666", "Columbus", "OH"),
        t("Oregon", "Ducks", "ORE", "goducks.com", "#154733", "#FEE123", "Eugene", "OR"),
        t("Penn State", "Nittany Lions", "PSU", "gopsusports.com", "#041E42", "#FFFFFF", "University Park", "PA"),
        t("Purdue", "Boilermakers", "PUR", "purduesports.com", "#CEB888", "#000000", "West Lafayette", "IN"),
        t("Rutgers", "Scarlet Knights", "RUT", "scarletknights.com", "#CC0033", "#FFFFFF", "Piscataway", "NJ"),
        t("UCLA", "Bruins", "UCLA", "uclabruins.com", "#2D68C4", "#F2A900", "Los Angeles", "CA"),
        t("USC", "Trojans", "USC", "usctrojans.com", "#990000", "#FFC72C", "Los Angeles", "CA"),
        t("Washington", "Huskies", "WASH", "gohuskies.com", "#4B2E83", "#B7A57A", "Seattle", "WA"),
    ]},

    # ====================== MID-MAJOR CONFERENCES ======================

    "mountain-west": {"name": "Mountain West Conference", "teams": [
        t("Air Force", "Falcons", "AFA", "goairforcefalcons.com", "#003087", "#8A8D8F", "Colorado Springs", "CO"),
        t("Fresno State", "Bulldogs", "FRES", "gobulldogs.com", "#DB0032", "#13294B", "Fresno", "CA"),
        t("Grand Canyon", "Antelopes", "GCU", "gculopes.com", "#522D80", "#FFFFFF", "Phoenix", "AZ"),
        t("Nevada", "Wolf Pack", "NEV", "nevadawolfpack.com", "#003366", "#A7A8AA", "Reno", "NV"),
        t("New Mexico", "Lobos", "UNM", "golobos.com", "#BA0C2F", "#A7A8AA", "Albuquerque", "NM"),
        t("New Mexico State", "Aggies", "NMSU", "nmstatesports.com", "#891216", "#000000", "Las Cruces", "NM"),
        t("San Diego State", "Aztecs", "SDSU", "goaztecs.com", "#A6192E", "#000000", "San Diego", "CA"),
        t("San Jose State", "Spartans", "SJSU", "sjsuspartans.com", "#0055A2", "#E5A823", "San Jose", "CA"),
        t("UNLV", "Rebels", "UNLV", "unlvrebels.com", "#CF0A2C", "#4D4D4F", "Las Vegas", "NV"),
        t("Washington State", "Cougars", "WSU", "wsucougars.com", "#981E32", "#5E6A71", "Pullman", "WA"),
        t("Wyoming", "Cowboys", "WYO", "gowyo.com", "#492F24", "#FFC425", "Laramie", "WY"),
    ]},

    "big-west": {"name": "Big West Conference", "teams": [
        t("Cal Poly", "Mustangs", "CP", "gopoly.com", "#1F4E3D", "#C4A13A", "San Luis Obispo", "CA"),
        t("UC Santa Barbara", "Gauchos", "UCSB", "ucsbgauchos.com", "#003660", "#FEBC11", "Santa Barbara", "CA"),
        t("Cal State Fullerton", "Titans", "CSUF", "fullertontitans.com", "#00274C", "#FF7900", "Fullerton", "CA"),
        t("Long Beach State", "Dirtbags", "LBSU", "longbeachstate.com", "#000000", "#F0AB00", "Long Beach", "CA"),
        t("UC Irvine", "Anteaters", "UCI", "ucirvinesports.com", "#0064A4", "#FFD200", "Irvine", "CA"),
        t("Hawaii", "Rainbow Warriors", "HAW", "hawaiiathletics.com", "#024731", "#FFFFFF", "Honolulu", "HI"),
        t("UC San Diego", "Tritons", "UCSD", "ucsdtritons.com", "#182B49", "#C69214", "La Jolla", "CA"),
        t("UC Riverside", "Highlanders", "UCR", "gohighlanders.com", "#003DA5", "#FFB81C", "Riverside", "CA"),
        t("Cal State Northridge", "Matadors", "CSUN", "gomatadors.com", "#CE1126", "#000000", "Northridge", "CA"),
        t("Cal State Bakersfield", "Roadrunners", "CSUB", "gorunners.com", "#003DA5", "#ED8B00", "Bakersfield", "CA"),
        t("UC Davis", "Aggies", "UCD", "ucdavisaggies.com", "#022851", "#FFBF00", "Davis", "CA"),
    ]},

    "sun-belt": {"name": "Sun Belt Conference", "teams": [
        t("Appalachian State", "Mountaineers", "APP", "appstatesports.com", "#000000", "#FFCC00", "Boone", "NC"),
        t("Arkansas State", "Red Wolves", "ARST", "astateredwolves.com", "#CC092F", "#000000", "Jonesboro", "AR"),
        t("Coastal Carolina", "Chanticleers", "CCU", "goccusports.com", "#006F71", "#A27752", "Conway", "SC"),
        t("Georgia Southern", "Eagles", "GASO", "gseagles.com", "#011E41", "#87714D", "Statesboro", "GA"),
        t("Georgia State", "Panthers", "GAST", "georgiastatesports.com", "#0039A6", "#CC0000", "Atlanta", "GA"),
        t("James Madison", "Dukes", "JMU", "jmusports.com", "#450084", "#CBB677", "Harrisonburg", "VA"),
        t("Louisiana", "Ragin Cajuns", "ULL", "ragincajuns.com", "#CE181E", "#FFFFFF", "Lafayette", "LA"),
        t("Louisiana-Monroe", "Warhawks", "ULM", "ulmwarhawks.com", "#800029", "#B3975A", "Monroe", "LA"),
        t("Marshall", "Thundering Herd", "MAR", "herdzone.com", "#00B140", "#FFFFFF", "Huntington", "WV"),
        t("Old Dominion", "Monarchs", "ODU", "odusports.com", "#003057", "#7C878E", "Norfolk", "VA"),
        t("South Alabama", "Jaguars", "USA", "usajaguars.com", "#003E7E", "#C41230", "Mobile", "AL"),
        t("Southern Miss", "Golden Eagles", "USM", "southernmiss.com", "#000000", "#FDD023", "Hattiesburg", "MS"),
        t("Texas State", "Bobcats", "TXST", "txstatebobcats.com", "#501214", "#8D734A", "San Marcos", "TX"),
        t("Troy", "Trojans", "TROY", "troytrojans.com", "#8B2332", "#000000", "Troy", "AL"),
    ]},

    # ====================== REMAINING CONFERENCES ======================

    "america-east": {"name": "America East Conference", "teams": [
        t("Albany", "Great Danes", "ALB", "ualbanysports.com", "#461D7C", "#EAAA00", "Albany", "NY"),
        t("Binghamton", "Bearcats", "BING", "bubearcats.com", "#005A43", "#FFFFFF", "Binghamton", "NY"),
        t("Bryant", "Bulldogs", "BRY", "bryantbulldogs.com", "#000000", "#C5B358", "Smithfield", "RI"),
        t("Maine", "Black Bears", "ME", "goblackbears.com", "#003263", "#FFFFFF", "Orono", "ME"),
        t("NJIT", "Highlanders", "NJIT", "njithighlanders.com", "#D22630", "#003DA5", "Newark", "NJ"),
        t("Stony Brook", "Seawolves", "SBU", "stonybrookathletics.com", "#990000", "#FFFFFF", "Stony Brook", "NY"),
        t("UMass Lowell", "River Hawks", "UML", "goriverhawks.com", "#003DA5", "#CC0000", "Lowell", "MA"),
        t("UMBC", "Retrievers", "UMBC", "umbcretrievers.com", "#000000", "#DEB230", "Baltimore", "MD"),
    ]},

    "aac": {"name": "American Athletic Conference", "teams": [
        t("Charlotte", "49ers", "CLT", "charlotte49ers.com", "#005035", "#A49665", "Charlotte", "NC"),
        t("East Carolina", "Pirates", "ECU", "ecupirates.com", "#592A8A", "#FFC72C", "Greenville", "NC"),
        t("FAU", "Owls", "FAU", "fausports.com", "#003366", "#CC0000", "Boca Raton", "FL"),
        t("Memphis", "Tigers", "MEM", "gotigersgo.com", "#003087", "#898D8D", "Memphis", "TN"),
        t("North Texas", "Mean Green", "UNT", "meangreensports.com", "#00853E", "#FFFFFF", "Denton", "TX"),
        t("Rice", "Owls", "RICE", "riceowls.com", "#002469", "#5E6A71", "Houston", "TX"),
        t("South Florida", "Bulls", "USF", "gousfbulls.com", "#006747", "#CFC493", "Tampa", "FL"),
        t("Tulane", "Green Wave", "TUL", "tulanegreenwave.com", "#006747", "#418FDE", "New Orleans", "LA"),
        t("UAB", "Blazers", "UAB", "uabsports.com", "#1E6B52", "#FFD700", "Birmingham", "AL"),
        t("UTSA", "Roadrunners", "UTSA", "goutsa.com", "#0C2340", "#F47321", "San Antonio", "TX"),
        t("Wichita State", "Shockers", "WICH", "goshockers.com", "#000000", "#FFC72C", "Wichita", "KS"),
    ]},

    "asun": {"name": "Atlantic Sun Conference", "teams": [
        t("Austin Peay", "Governors", "APSU", "letsgopeay.com", "#CC0000", "#FFFFFF", "Clarksville", "TN"),
        t("Bellarmine", "Knights", "BELL", "bellarmineathletics.com", "#003087", "#CC0000", "Louisville", "KY"),
        t("Central Arkansas", "Bears", "UCA", "ucasports.com", "#4F2D7F", "#A5A5A5", "Conway", "AR"),
        t("Eastern Kentucky", "Colonels", "EKU", "ekusports.com", "#861F41", "#FFFFFF", "Richmond", "KY"),
        t("FGCU", "Eagles", "FGCU", "fgcuathletics.com", "#003768", "#00B140", "Fort Myers", "FL"),
        t("Jacksonville", "Dolphins", "JU", "judolphins.com", "#006747", "#FFFFFF", "Jacksonville", "FL"),
        t("Lipscomb", "Bisons", "LIP", "lipscombsports.com", "#461D7C", "#B3A369", "Nashville", "TN"),
        t("North Alabama", "Lions", "UNA", "roarlions.com", "#461D7C", "#FFFFFF", "Florence", "AL"),
        t("Queens", "Royals", "QU", "queensathletics.com", "#002D72", "#8A8D8F", "Charlotte", "NC"),
        t("Stetson", "Hatters", "STET", "gohatters.com", "#006747", "#FFFFFF", "DeLand", "FL"),
    ]},

    "a10": {"name": "Atlantic 10 Conference", "teams": [
        t("Davidson", "Wildcats", "DAV", "davidsonwildcats.com", "#CC0000", "#000000", "Davidson", "NC"),
        t("Dayton", "Flyers", "DAY", "daytonflyers.com", "#CE1141", "#004B8D", "Dayton", "OH"),
        t("Fordham", "Rams", "FOR", "fordhamsports.com", "#7C2529", "#FFFFFF", "Bronx", "NY"),
        t("George Mason", "Patriots", "GMU", "gomason.com", "#006633", "#FFCC33", "Fairfax", "VA"),
        t("George Washington", "Revolutionaries", "GW", "gwsports.com", "#004065", "#B4985A", "Washington", "DC"),
        t("La Salle", "Explorers", "LAS", "goexplorers.com", "#003087", "#FFB81C", "Philadelphia", "PA"),
        t("UMass", "Minutemen", "MASS", "umassathletics.com", "#881C1C", "#000000", "Amherst", "MA"),
        t("Rhode Island", "Rams", "URI", "gorhody.com", "#002B5C", "#75B2DD", "Kingston", "RI"),
        t("Richmond", "Spiders", "RICH", "richmondspiders.com", "#990000", "#002B5C", "Richmond", "VA"),
        t("Saint Josephs", "Hawks", "SJU", "sjuhawks.com", "#9E1B34", "#FFFFFF", "Philadelphia", "PA"),
        t("Saint Louis", "Billikens", "SLU", "slubillikens.com", "#003DA5", "#FFFFFF", "St. Louis", "MO"),
        t("VCU", "Rams", "VCU", "vcuathletics.com", "#000000", "#F8B800", "Richmond", "VA"),
    ]},

    "big-east": {"name": "Big East Conference", "teams": [
        t("Butler", "Bulldogs", "BUT", "butlersports.com", "#13294B", "#FFFFFF", "Indianapolis", "IN"),
        t("UConn", "Huskies", "CONN", "uconnhuskies.com", "#000E2F", "#FFFFFF", "Storrs", "CT"),
        t("Creighton", "Bluejays", "CREI", "gocreighton.com", "#005CA9", "#FFFFFF", "Omaha", "NE"),
        t("Georgetown", "Hoyas", "GTWN", "guhoyas.com", "#041E42", "#8D817B", "Washington", "DC"),
        t("Seton Hall", "Pirates", "SH", "shupirates.com", "#004488", "#FFFFFF", "South Orange", "NJ"),
        t("St Johns", "Red Storm", "STJ", "redstormsports.com", "#CC0000", "#FFFFFF", "Queens", "NY"),
        t("Villanova", "Wildcats", "NOVA", "villanova.com", "#003366", "#FFFFFF", "Villanova", "PA"),
        t("Xavier", "Musketeers", "XAV", "goxavier.com", "#002969", "#9EA2A2", "Cincinnati", "OH"),
    ]},

    "big-south": {"name": "Big South Conference", "teams": [
        t("Charleston Southern", "Buccaneers", "CSU", "csbucs.com", "#003087", "#B4975A", "Charleston", "SC"),
        t("Gardner-Webb", "Runnin Bulldogs", "GWU", "gwusports.com", "#BF0D3E", "#000000", "Boiling Springs", "NC"),
        t("High Point", "Panthers", "HPU", "highpointpanthers.com", "#330072", "#FFFFFF", "High Point", "NC"),
        t("Longwood", "Lancers", "LONG", "longwoodlancers.com", "#003087", "#FFFFFF", "Farmville", "VA"),
        t("Presbyterian", "Blue Hose", "PRES", "gobluehose.com", "#003087", "#FFFFFF", "Clinton", "SC"),
        t("Radford", "Highlanders", "RAD", "radfordathletics.com", "#CC0000", "#003366", "Radford", "VA"),
        t("UNC Asheville", "Bulldogs", "UNCA", "uncabulldogs.com", "#003087", "#FFFFFF", "Asheville", "NC"),
        t("Winthrop", "Eagles", "WIN", "winthropeagles.com", "#8B2332", "#FFB81C", "Rock Hill", "SC"),
    ]},

    "caa": {"name": "Colonial Athletic Association", "teams": [
        t("Charleston", "Cougars", "COFC", "cofcsports.com", "#800000", "#FFFFFF", "Charleston", "SC"),
        t("Delaware", "Blue Hens", "DEL", "bluehens.com", "#00539F", "#FFD200", "Newark", "DE"),
        t("Drexel", "Dragons", "DREX", "drexeldragons.com", "#07294D", "#FFC600", "Philadelphia", "PA"),
        t("Elon", "Phoenix", "ELON", "elonphoenix.com", "#800000", "#B3A369", "Elon", "NC"),
        t("Hampton", "Pirates", "HAMP", "hamptonpirates.com", "#003087", "#FFFFFF", "Hampton", "VA"),
        t("Hofstra", "Pride", "HOF", "gohofstra.com", "#003087", "#FFD200", "Hempstead", "NY"),
        t("Monmouth", "Hawks", "MON", "monmouthhawks.com", "#003087", "#FFFFFF", "West Long Branch", "NJ"),
        t("NC A&T", "Aggies", "NCAT", "ncataggies.com", "#004684", "#FFB81C", "Greensboro", "NC"),
        t("Northeastern", "Huskies", "NEU", "nuhuskies.com", "#CC0000", "#000000", "Boston", "MA"),
        t("Towson", "Tigers", "TOW", "towsontigers.com", "#000000", "#FFB81C", "Towson", "MD"),
        t("UNC Wilmington", "Seahawks", "UNCW", "uncwsports.com", "#006666", "#FFD200", "Wilmington", "NC"),
        t("William & Mary", "Tribe", "WM", "tribeathletics.com", "#006747", "#B3A369", "Williamsburg", "VA"),
    ]},

    "cusa": {"name": "Conference USA", "teams": [
        t("FIU", "Panthers", "FIU", "fiusports.com", "#081E3F", "#B6862C", "Miami", "FL"),
        t("Jacksonville State", "Gamecocks", "JVST", "jsugamecocksports.com", "#CC0000", "#FFFFFF", "Jacksonville", "AL"),
        t("Kennesaw State", "Owls", "KSU", "ksuowls.com", "#000000", "#FDBB30", "Kennesaw", "GA"),
        t("Liberty", "Flames", "LIB", "libertyflames.com", "#002D62", "#CC0000", "Lynchburg", "VA"),
        t("Louisiana Tech", "Bulldogs", "LATECH", "latechsports.com", "#002F8B", "#CC0000", "Ruston", "LA"),
        t("Middle Tennessee", "Blue Raiders", "MTSU", "goblueraiders.com", "#0066CC", "#FFFFFF", "Murfreesboro", "TN"),
        t("Sam Houston", "Bearkats", "SHSU", "bearkatssports.com", "#F76900", "#FFFFFF", "Huntsville", "TX"),
        t("Western Kentucky", "Hilltoppers", "WKU", "wkusports.com", "#CC0000", "#FFFFFF", "Bowling Green", "KY"),
    ]},

    "horizon": {"name": "Horizon League", "teams": [
        t("Cleveland State", "Vikings", "CLEV", "csuvikings.com", "#006747", "#FFFFFF", "Cleveland", "OH"),
        t("Milwaukee", "Panthers", "MIL", "mkepanthers.com", "#000000", "#FFB81C", "Milwaukee", "WI"),
        t("Northern Kentucky", "Norse", "NKU", "nkunorse.com", "#000000", "#FFB81C", "Highland Heights", "KY"),
        t("Oakland", "Golden Grizzlies", "OAK", "goldengrizzlies.com", "#000000", "#B59A57", "Rochester", "MI"),
        t("Purdue Fort Wayne", "Mastodons", "PFW", "gomastodons.com", "#000000", "#CFB53B", "Fort Wayne", "IN"),
        t("Wright State", "Raiders", "WSU", "wsuraiders.com", "#007A33", "#CFB53B", "Dayton", "OH"),
        t("Youngstown State", "Penguins", "YSU", "ysusports.com", "#CC0000", "#FFFFFF", "Youngstown", "OH"),
    ]},

    "ivy": {"name": "Ivy League", "teams": [
        t("Brown", "Bears", "BRWN", "brownbears.com", "#4E3629", "#CC0000", "Providence", "RI"),
        t("Columbia", "Lions", "CLMB", "gocolumbialions.com", "#9BCBEB", "#002B7F", "New York", "NY"),
        t("Cornell", "Big Red", "COR", "cornellbigred.com", "#B31B1B", "#FFFFFF", "Ithaca", "NY"),
        t("Dartmouth", "Big Green", "DART", "dartmouthsports.com", "#00693E", "#FFFFFF", "Hanover", "NH"),
        t("Harvard", "Crimson", "HARV", "gocrimson.com", "#A51C30", "#FFFFFF", "Cambridge", "MA"),
        t("Penn", "Quakers", "PENN", "pennathletics.com", "#011F5B", "#990000", "Philadelphia", "PA"),
        t("Princeton", "Tigers", "PRIN", "goprincetontigers.com", "#FF8F00", "#000000", "Princeton", "NJ"),
        t("Yale", "Bulldogs", "YALE", "yalebulldogs.com", "#00356B", "#FFFFFF", "New Haven", "CT"),
    ]},

    "maac": {"name": "Metro Atlantic Athletic Conference", "teams": [
        t("Canisius", "Golden Griffins", "CAN", "gogriffs.com", "#002D72", "#FFB81C", "Buffalo", "NY"),
        t("Fairfield", "Stags", "FAIR", "fairfieldstags.com", "#CC0000", "#FFFFFF", "Fairfield", "CT"),
        t("Iona", "Gaels", "IONA", "icgaels.com", "#6A0032", "#FFD700", "New Rochelle", "NY"),
        t("Manhattan", "Jaspers", "MAN", "gojaspers.com", "#006747", "#FFFFFF", "Riverdale", "NY"),
        t("Marist", "Red Foxes", "MAR", "goredfoxes.com", "#CC0000", "#FFFFFF", "Poughkeepsie", "NY"),
        t("Niagara", "Purple Eagles", "NIAG", "purpleeagles.com", "#582C83", "#FFFFFF", "Lewiston", "NY"),
        t("Quinnipiac", "Bobcats", "QU", "quinnipiacbobcats.com", "#002B5C", "#FFB81C", "Hamden", "CT"),
        t("Rider", "Broncs", "RID", "gobroncs.com", "#8B2332", "#FFFFFF", "Lawrenceville", "NJ"),
        t("Saint Peters", "Peacocks", "SPU", "saintpeterspeacocks.com", "#003087", "#FFFFFF", "Jersey City", "NJ"),
        t("Siena", "Saints", "SIEN", "sienasaints.com", "#006747", "#FFD700", "Loudonville", "NY"),
    ]},

    "mac": {"name": "Mid-American Conference", "teams": [
        t("Ball State", "Cardinals", "BALL", "ballstatesports.com", "#CC0000", "#FFFFFF", "Muncie", "IN"),
        t("Bowling Green", "Falcons", "BGSU", "bgsufalcons.com", "#4F2C1D", "#FF7300", "Bowling Green", "OH"),
        t("Central Michigan", "Chippewas", "CMU", "cmuchippewas.com", "#6A0032", "#FFB81C", "Mt. Pleasant", "MI"),
        t("Eastern Michigan", "Eagles", "EMU", "emueagles.com", "#006747", "#FFFFFF", "Ypsilanti", "MI"),
        t("Kent State", "Golden Flashes", "KENT", "kentstatesports.com", "#002664", "#FFB81C", "Kent", "OH"),
        t("Miami Ohio", "RedHawks", "MIOH", "miamiredhawks.com", "#CC0000", "#FFFFFF", "Oxford", "OH"),
        t("Ohio", "Bobcats", "OHIO", "ohiobobcats.com", "#00694E", "#FFFFFF", "Athens", "OH"),
        t("Toledo", "Rockets", "TOL", "utrockets.com", "#002D62", "#FFB81C", "Toledo", "OH"),
        t("Western Michigan", "Broncos", "WMU", "wmubroncos.com", "#6C4023", "#FFB81C", "Kalamazoo", "MI"),
    ]},

    "meac": {"name": "Mid-Eastern Athletic Conference", "teams": [
        t("Coppin State", "Eagles", "COPP", "coppinstatesports.com", "#002D72", "#FFB81C", "Baltimore", "MD"),
        t("Delaware State", "Hornets", "DSU", "dsuhornets.com", "#CC0000", "#002B5C", "Dover", "DE"),
        t("Maryland-Eastern Shore", "Hawks", "UMES", "umeshawks.com", "#800000", "#FFFFFF", "Princess Anne", "MD"),
        t("Morgan State", "Bears", "MORG", "morganbears.com", "#F47920", "#003087", "Baltimore", "MD"),
        t("Norfolk State", "Spartans", "NSU", "nsuspartans.com", "#006747", "#FFB81C", "Norfolk", "VA"),
        t("NC Central", "Eagles", "NCCU", "nccueaglepride.com", "#800000", "#FFFFFF", "Durham", "NC"),
        t("SC State", "Bulldogs", "SCST", "scstateathletics.com", "#002D72", "#CC0000", "Orangeburg", "SC"),
    ]},

    "mvc": {"name": "Missouri Valley Conference", "teams": [
        t("Belmont", "Bruins", "BELM", "belmontbruins.com", "#002D62", "#CC0000", "Nashville", "TN"),
        t("Bradley", "Braves", "BRAD", "bradleybraves.com", "#CC0000", "#FFFFFF", "Peoria", "IL"),
        t("Dallas Baptist", "Patriots", "DBU", "dbupatriots.com", "#002D72", "#CC0000", "Dallas", "TX"),
        t("Evansville", "Purple Aces", "EVAN", "gopurpleaces.com", "#461D7C", "#F76900", "Evansville", "IN"),
        t("Illinois State", "Redbirds", "ILST", "goredbirds.com", "#CC0000", "#FFFFFF", "Normal", "IL"),
        t("Indiana State", "Sycamores", "INST", "gosycamores.com", "#003087", "#FFFFFF", "Terre Haute", "IN"),
        t("Missouri State", "Bears", "MOST", "missouristatebears.com", "#800000", "#FFFFFF", "Springfield", "MO"),
        t("Murray State", "Racers", "MURR", "goracers.com", "#002D72", "#FFB81C", "Murray", "KY"),
        t("Southern Illinois", "Salukis", "SIU", "salukis.com", "#800000", "#FFFFFF", "Carbondale", "IL"),
        t("UIC", "Flames", "UIC", "uicflames.com", "#CC0000", "#001E62", "Chicago", "IL"),
        t("Valparaiso", "Beacons", "VALP", "valpoathletics.com", "#613318", "#FFB81C", "Valparaiso", "IN"),
    ]},

    "nec": {"name": "Northeast Conference", "teams": [
        t("Central Connecticut", "Blue Devils", "CCSU", "ccsubluedevils.com", "#003087", "#FFFFFF", "New Britain", "CT"),
        t("Fairleigh Dickinson", "Knights", "FDU", "fduknights.com", "#003087", "#CC0000", "Teaneck", "NJ"),
        t("Le Moyne", "Dolphins", "LEM", "lemoynedolphins.com", "#006747", "#FFFFFF", "Syracuse", "NY"),
        t("LIU", "Sharks", "LIU", "liuathletics.com", "#003087", "#FFB81C", "Brooklyn", "NY"),
        t("Merrimack", "Warriors", "MERR", "merrimackathletics.com", "#002D72", "#FFB81C", "North Andover", "MA"),
        t("Mount St Marys", "Mountaineers", "MSM", "mountathletics.com", "#003087", "#FFFFFF", "Emmitsburg", "MD"),
        t("Sacred Heart", "Pioneers", "SHU", "sacredheartpioneers.com", "#CC0000", "#FFFFFF", "Fairfield", "CT"),
        t("Stonehill", "Skyhawks", "STON", "stonehillskyhawks.com", "#461D7C", "#FFFFFF", "Easton", "MA"),
        t("Wagner", "Seahawks", "WAG", "wagnerathletics.com", "#006747", "#FFFFFF", "Staten Island", "NY"),
    ]},

    "ovc": {"name": "Ohio Valley Conference", "teams": [
        t("Eastern Illinois", "Panthers", "EIU", "eiupanthers.com", "#003087", "#FFFFFF", "Charleston", "IL"),
        t("Lindenwood", "Lions", "LIND", "lindenwoodlions.com", "#000000", "#FFB81C", "St. Charles", "MO"),
        t("Little Rock", "Trojans", "LR", "lrtrojans.com", "#CC0000", "#FFFFFF", "Little Rock", "AR"),
        t("Morehead State", "Eagles", "MORE", "msueagles.com", "#003087", "#FFB81C", "Morehead", "KY"),
        t("SE Missouri State", "Redhawks", "SEMO", "gosoutheast.com", "#CC0000", "#000000", "Cape Girardeau", "MO"),
        t("Southern Indiana", "Screaming Eagles", "USI", "usieagles.com", "#CC0000", "#003087", "Evansville", "IN"),
        t("Tennessee State", "Tigers", "TNST", "tsutigers.com", "#003087", "#FFFFFF", "Nashville", "TN"),
        t("Tennessee Tech", "Golden Eagles", "TTU", "ttusports.com", "#461D7C", "#FFB81C", "Cookeville", "TN"),
        t("UT Martin", "Skyhawks", "UTM", "utmsports.com", "#F76900", "#002D62", "Martin", "TN"),
    ]},

    "patriot": {"name": "Patriot League", "teams": [
        t("Army", "Black Knights", "ARMY", "goarmywestpoint.com", "#000000", "#FFB81C", "West Point", "NY"),
        t("Bucknell", "Bison", "BUCK", "bucknellbison.com", "#F76900", "#003087", "Lewisburg", "PA"),
        t("Holy Cross", "Crusaders", "HC", "goholycross.com", "#602D89", "#FFFFFF", "Worcester", "MA"),
        t("Lafayette", "Leopards", "LAF", "goleopards.com", "#800000", "#FFFFFF", "Easton", "PA"),
        t("Lehigh", "Mountain Hawks", "LEH", "lehighsports.com", "#653819", "#FFFFFF", "Bethlehem", "PA"),
        t("Navy", "Midshipmen", "NAVY", "navysports.com", "#002D72", "#FFB81C", "Annapolis", "MD"),
    ]},

    "socon": {"name": "Southern Conference", "teams": [
        t("Chattanooga", "Mocs", "UTC", "gomocs.com", "#002D72", "#FFB81C", "Chattanooga", "TN"),
        t("ETSU", "Buccaneers", "ETSU", "etsubucs.com", "#002D72", "#FFB81C", "Johnson City", "TN"),
        t("Furman", "Paladins", "FUR", "furmanpaladins.com", "#582C83", "#FFFFFF", "Greenville", "SC"),
        t("Mercer", "Bears", "MER", "mercerbears.com", "#F76900", "#000000", "Macon", "GA"),
        t("Samford", "Bulldogs", "SAM", "samfordsports.com", "#002D72", "#CC0000", "Birmingham", "AL"),
        t("The Citadel", "Bulldogs", "CIT", "citadelsports.com", "#003087", "#FFFFFF", "Charleston", "SC"),
        t("UNC Greensboro", "Spartans", "UNCG", "uncgspartans.com", "#003087", "#FFB81C", "Greensboro", "NC"),
        t("VMI", "Keydets", "VMI", "vmikeydets.com", "#CC0000", "#FFB81C", "Lexington", "VA"),
        t("Western Carolina", "Catamounts", "WCU", "catamountsports.com", "#592C82", "#C5B358", "Cullowhee", "NC"),
        t("Wofford", "Terriers", "WOF", "woffordterriers.com", "#000000", "#886B25", "Spartanburg", "SC"),
    ]},

    "southland": {"name": "Southland Conference", "teams": [
        t("Houston Christian", "Huskies", "HCU", "hcuhuskies.com", "#F76900", "#003087", "Houston", "TX"),
        t("Incarnate Word", "Cardinals", "UIW", "uiwcardinals.com", "#CC0000", "#000000", "San Antonio", "TX"),
        t("McNeese", "Cowboys", "MCN", "mcneesesports.com", "#003087", "#FFB81C", "Lake Charles", "LA"),
        t("New Orleans", "Privateers", "UNO", "unoprivateers.com", "#003087", "#A5A5A5", "New Orleans", "LA"),
        t("Nicholls", "Colonels", "NICH", "geauxcolonels.com", "#CC0000", "#FFFFFF", "Thibodaux", "LA"),
        t("Northwestern State", "Demons", "NWST", "naborathletics.com", "#461D7C", "#F76900", "Natchitoches", "LA"),
        t("SE Louisiana", "Lions", "SELA", "lionsports.net", "#006747", "#FFB81C", "Hammond", "LA"),
        t("Texas A&M-Corpus Christi", "Islanders", "AMCC", "goislanders.com", "#003087", "#006747", "Corpus Christi", "TX"),
    ]},

    "summit": {"name": "Summit League", "teams": [
        t("Kansas City", "Roos", "UMKC", "umkcroos.com", "#003087", "#FFB81C", "Kansas City", "MO"),
        t("North Dakota State", "Bison", "NDSU", "gobison.com", "#006747", "#FFB81C", "Fargo", "ND"),
        t("Omaha", "Mavericks", "OMA", "omavs.com", "#000000", "#CC0000", "Omaha", "NE"),
        t("Oral Roberts", "Golden Eagles", "ORU", "orugoldeneagles.com", "#002D72", "#FFB81C", "Tulsa", "OK"),
        t("South Dakota State", "Jackrabbits", "SDSU", "gojacks.com", "#003087", "#FFB81C", "Brookings", "SD"),
        t("Western Illinois", "Leathernecks", "WIU", "goleathernecks.com", "#461D7C", "#FFB81C", "Macomb", "IL"),
    ]},

    "swac": {"name": "Southwestern Athletic Conference", "teams": [
        t("Alabama A&M", "Bulldogs", "AAMU", "aamusports.com", "#800000", "#FFFFFF", "Normal", "AL"),
        t("Alabama State", "Hornets", "ALST", "bamastatesports.com", "#000000", "#FFB81C", "Montgomery", "AL"),
        t("Alcorn State", "Braves", "ALCN", "alcornsports.com", "#461D7C", "#FFB81C", "Lorman", "MS"),
        t("Arkansas-Pine Bluff", "Golden Lions", "UAPB", "uapblionsroar.com", "#000000", "#FFB81C", "Pine Bluff", "AR"),
        t("Bethune-Cookman", "Wildcats", "BCU", "bcuathletics.com", "#800000", "#FFB81C", "Daytona Beach", "FL"),
        t("Florida A&M", "Rattlers", "FAMU", "famuathletics.com", "#F76900", "#006747", "Tallahassee", "FL"),
        t("Grambling State", "Tigers", "GRAM", "gsutigers.com", "#000000", "#FFB81C", "Grambling", "LA"),
        t("Jackson State", "Tigers", "JKST", "jsutigers.com", "#003087", "#FFFFFF", "Jackson", "MS"),
        t("Mississippi Valley State", "Delta Devils", "MVSU", "mvsusports.com", "#006747", "#FFFFFF", "Itta Bena", "MS"),
        t("Prairie View A&M", "Panthers", "PVAM", "pvpantherathletics.com", "#461D7C", "#FFB81C", "Prairie View", "TX"),
        t("Southern University", "Jaguars", "SOU", "gojagsports.com", "#003087", "#FFB81C", "Baton Rouge", "LA"),
        t("Texas Southern", "Tigers", "TXSO", "tsusports.com", "#800000", "#FFFFFF", "Houston", "TX"),
    ]},

    "wac": {"name": "Western Athletic Conference", "teams": [
        t("Abilene Christian", "Wildcats", "ACU", "acusports.com", "#461D7C", "#FFFFFF", "Abilene", "TX"),
        t("California Baptist", "Lancers", "CBU", "golancers.com", "#002D72", "#FFB81C", "Riverside", "CA"),
        t("Seattle U", "Redhawks", "SEA", "goseattleu.com", "#CC0000", "#FFFFFF", "Seattle", "WA"),
        t("Southern Utah", "Thunderbirds", "SUU", "suutbirds.com", "#CC0000", "#002D72", "Cedar City", "UT"),
        t("Stephen F Austin", "Lumberjacks", "SFA", "sfajacks.com", "#461D7C", "#FFFFFF", "Nacogdoches", "TX"),
        t("Tarleton State", "Texans", "TAR", "tarletonsports.com", "#461D7C", "#FFFFFF", "Stephenville", "TX"),
        t("UT Arlington", "Mavericks", "UTA", "utamavs.com", "#003087", "#F76900", "Arlington", "TX"),
        t("Utah Tech", "Trailblazers", "UTCH", "utahtechtrailblazers.com", "#CC0000", "#003087", "St. George", "UT"),
        t("Utah Valley", "Wolverines", "UVU", "wolverinegreen.com", "#275D38", "#FFFFFF", "Orem", "UT"),
    ]},

    "wcc": {"name": "West Coast Conference", "teams": [
        t("Gonzaga", "Bulldogs", "GONZ", "gonzagabulldogs.com", "#002967", "#C8102E", "Spokane", "WA"),
        t("LMU", "Lions", "LMU", "lmulions.com", "#8B2332", "#003087", "Los Angeles", "CA"),
        t("Pacific", "Tigers", "PAC", "pacifictigers.com", "#F47920", "#000000", "Stockton", "CA"),
        t("Pepperdine", "Waves", "PEPP", "pepperdinewaves.com", "#003087", "#F76900", "Malibu", "CA"),
        t("Portland", "Pilots", "PORT", "portlandpilots.com", "#461D7C", "#FFFFFF", "Portland", "OR"),
        t("Saint Marys", "Gaels", "SMC", "smcgaels.com", "#CC0000", "#003087", "Moraga", "CA"),
        t("San Diego", "Toreros", "USD", "usdtoreros.com", "#002D72", "#89CFF0", "San Diego", "CA"),
        t("San Francisco", "Dons", "USF", "usfdons.com", "#006747", "#FFB81C", "San Francisco", "CA"),
        t("Santa Clara", "Broncos", "SCU", "santaclarabroncos.com", "#862633", "#FFFFFF", "Santa Clara", "CA"),
    ]},

    "pac-12": {"name": "Pac-12 Conference", "teams": [
        t("Oregon State", "Beavers", "ORST", "osubeavers.com", "#DC4405", "#000000", "Corvallis", "OR"),
    ]},
}


def generate_team_config(team, conference_name):
    """Generate a full config entry from minimal team data."""
    domain = team["domain"]
    base_url = f"https://{domain}"
    team_id = (
        team["name"].lower()
        .replace(" ", "-").replace("&", "and").replace("'", "")
        .replace(".", "").replace("–", "-").replace("(", "").replace(")", "")
    )
    return {
        "id": team_id,
        "name": team["name"],
        "mascot": team["mascot"],
        "abbreviation": team["abbr"],
        "primary_color": team["colors"][0],
        "secondary_color": team["colors"][1],
        "head_coach": "",
        "stadium": "",
        "city": team.get("city", ""),
        "state": team.get("state", ""),
        "site_provider": "sidearm",
        "base_url": base_url,
        "roster_url": f"{base_url}/sports/baseball/roster",
        "schedule_url": f"{base_url}/sports/baseball/schedule/2026",
        "stats_url": f"{base_url}/sports/baseball/stats",
        "logo_url": f"{base_url}/images/logos/site/site.png"
    }


def verify_url(url, timeout=10):
    if not HAS_REQUESTS: return None
    try:
        r = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return r.status_code == 200
    except:
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True, stream=True)
            return r.status_code == 200
        except:
            return False


def build_config(target_conferences=None, verify=False):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "teams.json")
    config = {"conferences": {}}

    conferences_to_add = target_conferences or list(ALL_CONFERENCES.keys())
    total_added = 0
    failed = []

    for conf_id in conferences_to_add:
        if conf_id not in ALL_CONFERENCES:
            print(f"⚠️  Unknown: {conf_id}. Available: {', '.join(ALL_CONFERENCES.keys())}")
            continue

        conf = ALL_CONFERENCES[conf_id]
        print(f"\n{'='*55}")
        print(f"📋 {conf['name']} ({len(conf['teams'])} teams)")
        print(f"{'='*55}")

        teams = []
        for team in conf["teams"]:
            tc = generate_team_config(team, conf["name"])

            if verify:
                print(f"  {team['name']:30s}", end="", flush=True)
                ok = verify_url(tc["roster_url"])
                if ok: print(" ✅")
                elif ok is None: print(" ⏭️  (no requests)")
                else:
                    print(f" ❌ {tc['roster_url']}")
                    failed.append((team["name"], tc["roster_url"]))
                time.sleep(0.3)
            else:
                print(f"  ✅ {team['name']}")

            teams.append(tc)
            total_added += 1

        # Create output directory for this conference
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", conf_id)
        os.makedirs(out_dir, exist_ok=True)

        config["conferences"][conf_id] = {"name": conf["name"], "teams": teams}

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    total_confs = len(config["conferences"])
    print(f"\n{'='*55}")
    print(f"✅ CONFIG SAVED: {config_path}")
    print(f"   {total_confs} conferences | {total_added} teams")
    print(f"{'='*55}")
    for cid, cd in config["conferences"].items():
        print(f"   {cd['name']:40s} {len(cd['teams']):3d} teams")

    if failed:
        print(f"\n⚠️  {len(failed)} URLs failed:")
        for n, u in failed:
            print(f"   {n}: {u}")

    print(f"\n🚀 Ready! Try:  python3 main.py --list")


def list_all():
    total = 0
    for cid, cd in ALL_CONFERENCES.items():
        print(f"\n{cd['name'].upper()} ({len(cd['teams'])})")
        print("-" * 55)
        for t in cd["teams"]:
            print(f"  {t['abbr']:6s} {t['name']:30s} {t['domain']}")
            total += 1
    print(f"\n{'='*55}")
    print(f"TOTAL: {total} teams across {len(ALL_CONFERENCES)} conferences")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Build PressBox config for ALL D1 baseball")
    p.add_argument("--verify", action="store_true", help="Verify URLs")
    p.add_argument("--conference", type=str, help="Only one conference")
    p.add_argument("--list", action="store_true", help="List all and exit")
    args = p.parse_args()

    if args.list: list_all()
    else: build_config([args.conference] if args.conference else None, args.verify)
