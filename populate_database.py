import os
import django
import re
import unicodedata
import json

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "player_chain.settings")
django.setup()

from playergame.models import Player

def read_player_data(filename):
    # Open and read the player data file
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Use regex to split data by player entries
    players = re.findall(r"Player Name: .+?(?=\nPlayer Name: |\Z)", content, re.DOTALL)
    player_data = {}
    names_count = {}  # Dictionary to count occurrences of normalized names

    # First pass: Count occurrences of each normalized name and collect positions
    for player in players:
        details = re.search(r"Player Name: (.+?)\nWikipedia URL: (.+?)\n(.+)", player, re.DOTALL)
        original_name = details.group(1).strip()

        # Normalize the player's name
        normalized_name = normalize_name(original_name)

        # Count occurrences of normalized names
        names_count[normalized_name] = names_count.get(normalized_name, 0) + 1

    # Second pass: Process each player and append positions where needed
    for player in players:
        details = re.search(r"Player Name: (.+?)\nWikipedia URL: (.+?)\n(.+)", player, re.DOTALL)
        original_name = details.group(1).strip()
        wiki_url = details.group(2).strip()
        full_record = details.group(3).strip()

        # Parse player data
        age = parse_age(full_record)
        position = parse_position(full_record)
        position = position if position else "Unknown"
        youth_career = parse_career(full_record, "Youth Career")
        club_career = parse_career(full_record, "Senior Career")
        intl_career = parse_career(full_record, "International Career")
        managerial_career = parse_career(full_record, "Managerial Career")

        # Normalize the player's name
        normalized_name = normalize_name(original_name)

        # Handle duplicates by appending the position
        if names_count[normalized_name] > 1:
            original_name = f"{original_name} ({position})"
            normalized_name = normalize_name(original_name)

        # Warn about overwriting data for the same normalized name
        if normalized_name in player_data:
            print(f"Warning: Overwriting player data for '{original_name}' with normalized name '{normalized_name}'")

        # Store player data
        player_data[normalized_name] = {
            'original_name': original_name,
            'wiki_url': wiki_url,
            'full_record': full_record,
            'age': age,
            'position': position,
            'club_career': json.dumps(club_career),  # Convert list to JSON
            'intl_career': json.dumps(intl_career),  # Convert list to JSON
            'youth_career': json.dumps(youth_career), # Convert list to JSON
            'managerial_career': json.dumps(managerial_career) # Convert list to JSON
        }

    return player_data


def normalize_name(name):
    # Normalize the name by converting to ASCII and lowercase
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = re.sub(r"[^\w\s']", '', name).lower().replace(" ", "")
    return name

def parse_career(record, section_header):
    # Parse different career sections (Youth, Senior, International, Managerial)
    section_found = False
    career = []
    for line in record.split("\n"):
        line = line.strip()
        if line == section_header:
            section_found = True
            continue
        if section_found:
            if line and ":" in line and not line.startswith("Date of Birth") and not line.startswith("Place of Birth") and not line.startswith("Height") and not line.startswith("Position"):
                parts = line.split(":")
                if len(parts) == 2:
                    season, squad = parts[0].strip(), parts[1].strip().replace("(loan)", "").strip()
                    career.append((season, squad))
            elif not line or "Career" in line:
                break
    return career

def parse_age(record):
    # Extract the player's age
    match = re.search(r"Date of Birth: .+?\((\d+)-\d+-\d+\)", record)
    return int(match.group(1)) if match else None

def parse_position(record):
    # Extract the player's position(s), accounting for possible variations like "Position(s):"
    match = re.search(r"Position\(s\)?: (.+)", record)
    return match.group(1).strip() if match else None
def populate_database(player_data):
    # Clear existing data and populate new data
    Player.objects.all().delete()
    for normalized_name, data in player_data.items():
        try:
            Player.objects.create(
                normalized_name=normalized_name,
                original_name=data['original_name'],
                wiki_url=data['wiki_url'],
                full_record=data['full_record'],
                age=data['age'],
                position=data['position'],
                club_career=data['club_career'],
                intl_career=data['intl_career'],
                youth_career=data['youth_career'],
                managerial_career=data['managerial_career']
            )
        except Exception as e:
            print(f"Error saving player {data['original_name']}: {e}")

if __name__ == "__main__":
    filename = r"C:\Users\karum\greenlinks\unique_player_stats.txt"
    player_data = read_player_data(filename)
    populate_database(player_data)
    print("Database population complete.")
