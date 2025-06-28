# management/commands/precompute_games.py

import json
import random
import itertools
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from playergame.models import DailyGame, GameSession
from playergame.utils import precompute_links, load_and_preprocess_player_data


class Command(BaseCommand):
    help = 'Precompute game rounds for the next set of days (e.g., 90 days)'

    USED_PAIRS_FILE = Path('used_pairs.txt')
    TIERS_CONFIG_FILE = Path('player_tiers.json')
    DAYS_AHEAD = 90

    def handle(self, *args, **kwargs):
        # Load player data and tier configuration
        player_data = load_and_preprocess_player_data()
        if not self.TIERS_CONFIG_FILE.exists():
            self.stderr.write(self.style.ERROR(
                f"Tier config not found: {self.TIERS_CONFIG_FILE}. "
                "Please create a JSON file with keys 'current_popular', 'current_normal', 'older_popular'."
            ))
            return

        with open(self.TIERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            tiers = json.load(f)

        popular = tiers.get('current_popular', [])
        normal  = tiers.get('current_normal', [])
        older   = tiers.get('older_popular', [])

        # Prepare all possible combinations, shuffle once
        combos = {
            1: list(itertools.combinations(popular, 2)),
            2: list(itertools.product(popular, normal)),
            3: list(itertools.product(popular, older)),
        }
        for c in combos.values():
            random.shuffle(c)

        # Load already used pairs
        used_pairs = set()
        if self.USED_PAIRS_FILE.exists():
            used_pairs = set(self.USED_PAIRS_FILE.read_text(encoding='utf-8').splitlines())

        new_used = set()

        # Clear old sessions if needed
        GameSession.objects.all().delete()

        # Define per-round requirements
        required_lengths   = [2, 3, 3]
        link_type_options  = [
            ['both', 'club', 'national'],
            ['both', 'club', 'national'],
            ['club', 'both', 'national'],
        ]

        # Generate games for each day
        for offset in range(self.DAYS_AHEAD):
            game_date = timezone.now().date() + timezone.timedelta(days=offset)
            daily_pairs = []

            for round_no in (1, 2, 3):
                combo_list = combos[round_no]
                needed_len = required_lengths[round_no - 1]
                round_link_types = link_type_options[round_no - 1]
                found = False

                for raw_pair in combo_list:
                    pair = tuple(sorted(raw_pair))
                    key = f"{pair[0]}|{pair[1]}"
                    if key in used_pairs or key in new_used:
                        continue

                    # Try each link type until we hit the target length
                    for lt in round_link_types:
                        links = precompute_links([pair], player_data, [lt])
                        if links and len(links[0]) == needed_len:
                            daily_pairs.append(pair)
                            new_used.add(key)
                            found = True
                            break
                    if found:
                        break

                if not found:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️ {game_date}: no round {round_no} with exact length {needed_len}"
                    ))

            # If we have at least one pair, save them
            if daily_pairs:
                # Use the first choice of link-type for storage
                chosen_link_types = [opts[0] for opts in link_type_options]
                precomputed = precompute_links(daily_pairs, player_data, chosen_link_types)

                DailyGame.objects.update_or_create(
                    date=game_date,
                    defaults={
                        'player_pairs':     daily_pairs,
                        'precomputed_links': precomputed,
                        'link_types':       chosen_link_types,
                    }
                )
                self.stdout.write(
                    f"✅ {game_date}: stored {len(daily_pairs)} rounds"
                )

        # Append newly used pairs to disk
        if new_used:
            with open(self.USED_PAIRS_FILE, 'a', encoding='utf-8') as f:
                for key in sorted(new_used):
                    f.write(key + "\n")

        self.stdout.write(self.style.SUCCESS(
            f"Finished precomputing {self.DAYS_AHEAD} days of games."
        ))
