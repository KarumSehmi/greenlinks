# myapp/utils.py

from playergame.views import bfs_bidirectional  # Assuming bfs_bidirectional is in views.py
from playergame.models import Player  # Import the Player model
import unicodedata
import re
import json

# Function to find common teams
def find_common_teams(player1_career, player2_career):
    return player1_career & player2_career

# Normalize player names
def normalize_name(name):
    """Normalize player names for consistent key usage, handling diacritical marks."""
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = re.sub(r'[^a-zA-Z0-9]', '', name)  # Remove non-alphanumeric characters
    return name.lower()



def precompute_links(player_pairs, player_data, link_types):
    precomputed_links = []
    
    for index, (start_player, end_player) in enumerate(player_pairs):
        current_link_type = link_types[index]
        #print(f"Computing link for: {start_player} -> {end_player} with link type: {current_link_type}")

        # Normalize player names
        normalized_start = normalize_name(start_player)
        normalized_end = normalize_name(end_player)

        # Check if both players exist in the player_data
        if normalized_start not in player_data or normalized_end not in player_data:
            #print(f"Player data not found for {start_player} or {end_player}. Skipping this pair.")
            continue

        # Compute the shortest link using bfs_bidirectional
        shortest_link = bfs_bidirectional(player_data, normalized_start, normalized_end, current_link_type)

        # Debugging to check if the shortest link is found
        if not shortest_link:
            #print(f"No valid link found between {start_player} and {end_player} with link type: {current_link_type}")
            continue

        link_details = []
        for i in range(len(shortest_link) - 1):
            player = player_data[shortest_link[i]]
            next_player = player_data[shortest_link[i + 1]]
            
            # Find common teams between players
            common_clubs = find_common_teams(player['club_career'], next_player['club_career'])
            common_intl = find_common_teams(player['intl_career'], next_player['intl_career'])

            formatted_common_clubs = [{'season': club[0], 'team': club[1]} for club in common_clubs]
            formatted_common_intl = [{'season': intl[0], 'team': intl[1]} for intl in common_intl]

            link_details.append({
                'player': player['original_name'],
                'next_player': next_player['original_name'],
                'common_clubs': formatted_common_clubs,
                'common_intl': formatted_common_intl if current_link_type != 'club' else []
            })
        
        #print(f"Precomputed link details for {start_player} -> {end_player}: {link_details}")
        precomputed_links.append(link_details)

    #print(f"Final Precomputed Links: {precomputed_links}")
    return precomputed_links

# Load and preprocess player data
def load_and_preprocess_player_data():
    players = Player.objects.all()
    player_data = {}
    for player in players:
        try:
            club_career = json.loads(player.club_career)
            intl_career = json.loads(player.intl_career)

            processed_club_career = []
            for club in club_career:
                # Process the club career data
                if len(club) == 2:
                    season, *club_name_parts = club[0].split(maxsplit=1)
                    club_name = " ".join(club_name_parts + [club[1]]) if club_name_parts else club[1]
                else:
                    season = "Unknown Season"
                    club_name = " ".join(club)  # Fallback to combining all parts

                processed_club_career.append((season, club_name))

            processed_intl_career = []
            for intl in intl_career:
                # Process the international career data similarly to club career
                if len(intl) == 2:
                    season, *team_name_parts = intl[0].split(maxsplit=1)
                    team_name = " ".join(team_name_parts + [intl[1]]) if team_name_parts else intl[1]
                else:
                    season = "Unknown Season"
                    team_name = " ".join(intl)  # Fallback to combining all parts

                processed_intl_career.append((season, team_name))

        except Exception as e:
            #print(f"Error parsing career data for player {player.original_name}: {e}")
            processed_club_career = []
            processed_intl_career = []

        normalized_name = normalize_name(player.original_name)
        player_data[normalized_name] = {
            'club_career': set(processed_club_career),
            'intl_career': set(processed_intl_career),
            'original_name': player.original_name
        }

    return player_data
