import json
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from playergame.models import Player
from playergame.views import normalize_name, load_and_preprocess_player_data
from django.test.client import Client


class Command(BaseCommand):
    help = 'Finds interesting links between top 500 players for the football linking chain game.'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        logging.info('Loading player data...')
        player_data = load_and_preprocess_player_data()

        # Load the top 500 players from the file and normalize their names
        top_500_players = self.load_top_500_players('C:/Users/karum/greenlinks/playergame/top_500_football_players_names.txt')
        normalized_top_500 = set(normalize_name(player) for player in top_500_players)
        
        # Filter player data to only include top 500 players
        filtered_player_data = {name: data for name, data in player_data.items() if name in normalized_top_500}
        all_players = list(filtered_player_data.keys())
        interesting_links = []

        logging.info(f'Total players to process: {len(all_players)}')
        min_common_teams = 3  # Example criterion: Minimum number of common teams

        # Iterate over the player pairs
        for i in range(len(all_players)):
            start_player = all_players[i]

            for j in range(i + 1, len(all_players)):
                end_player = all_players[j]

                # Log the current player pair being processed
                logging.info(f'Processing link between {start_player} and {end_player}...')

                link_data = self.find_interesting_link(start_player, end_player, filtered_player_data, min_common_teams)

                if link_data:
                    logging.info(f'Found interesting link: {link_data}')
                    interesting_links.append(link_data)

        logging.info('Saving interesting links...')
        self.save_interesting_links(interesting_links)
        logging.info('Finished processing.')

    def load_top_500_players(self, filepath):
        """Load the top 500 players from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            logging.error(f"File not found: {filepath}")
            return []

    def find_interesting_link(self, start_player, end_player, player_data, min_common_teams):
        """Find an interesting link between two players."""
        logging.info(f'Finding link between {start_player} and {end_player}')
        normalized_start_player = normalize_name(start_player)
        normalized_end_player = normalize_name(end_player)

        link_data = find_link_helper(normalized_start_player, normalized_end_player, 'both', player_data)

        # Check if the link has 3 or more steps (4 players)
        if link_data['link_details'] and len(link_data['link_details']) >= 3:
            total_common_teams = sum(len(link['common_clubs']) + len(link['common_intl']) for link in link_data['link_details'])

            if total_common_teams >= min_common_teams:
                return {
                    'start_player': start_player,
                    'end_player': end_player,
                    'link_details': link_data['link_details'],
                    'total_common_teams': total_common_teams
                }
        return None

    def save_interesting_links(self, interesting_links):
        """Save the interesting links to a file."""
        today = timezone.now().date()
        file_name = f"interesting_links_{today}.json"

        with open(file_name, 'w') as f:
            json.dump(interesting_links, f)

        self.stdout.write(self.style.SUCCESS(f'Successfully found and saved {len(interesting_links)} interesting links.'))


def find_link_helper(start_player, end_player, link_type, player_data):
    """Helper function to find a link between two players."""
    from django.test.client import Client
    import json

    client = Client()
    response = client.get('/find_link/', {'start_player': start_player, 'end_player': end_player, 'link_type': link_type})

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        print(f"Error finding link between {start_player} and {end_player}: {response.content}")
        return {'link_details': None, 'is_optimal': False}
