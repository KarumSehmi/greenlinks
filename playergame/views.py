
from django.shortcuts import render
from django.http import JsonResponse
from .models import Player
import difflib
from collections import defaultdict
import unicodedata
import json
import heapq
import time
import random
import re
import logging
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
logger = logging.getLogger(__name__)
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache


from django.http import FileResponse
from django.conf import settings
import os
def robots_txt(request):
    filepath = os.path.join(settings.BASE_DIR, 'robots.txt')
    return FileResponse(open(filepath, 'rb'), content_type='text/plain')



def rules(request):
    context = {}
    # Specify the full path to the template including the app name
    return render(request, 'playergame/rules.html', context)


def home(request):

    return render(request, 'playergame/player_chain.html')

def index(request):
    return render(request, 'playergame/index.html')



from django.http import JsonResponse
from django.utils import timezone
from playergame.models import DailyGame

def start_game(request):
    round_number = int(request.GET.get('round', 0))

    
    allow_multiple_links = request.GET.get('allow_multiple_links', 'false').lower() == 'true'
    
    today = timezone.now().date()
    
    try:
        daily_game = DailyGame.objects.get(date=today)
        if round_number < len(daily_game.player_pairs):
          
            start_player, end_player = daily_game.player_pairs[round_number]
            link_type = daily_game.link_types[round_number]

        else:
            return JsonResponse({'error': 'Round number out of range.'}, status=400)

        data = {
            'start_player': start_player,
            'end_player': end_player,
            'precomputed_links': daily_game.precomputed_links[round_number],
            'link_type': link_type,
            'allow_multiple_links': allow_multiple_links
        }
        return JsonResponse(data)
    except DailyGame.DoesNotExist:
        return JsonResponse({'error': 'Daily game data not found for today.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import GameSession
import json



@csrf_exempt
@require_http_methods(["POST"])
def save_game_state(request):
    data = json.loads(request.body)
    session_id = data.get('session_id')
    
    game_session, created = GameSession.objects.get_or_create(session_id=session_id)
    game_session.current_round = data.get('current_round', 0)
    game_session.score = data.get('score', 0)
    game_session.lives_remaining = data.get('lives_remaining', 3)
    game_session.start_player = data.get('start_player', '')
    game_session.end_player = data.get('end_player', '')
    game_session.link_type = data.get('link_type', '')
    game_session.intermediate_players = data.get('intermediate_players', [])
    game_session.previous_guesses = data.get('previous_guesses', [])
    game_session.round_scores = data.get('round_scores', [])
    game_session.is_game_won = data.get('is_game_won', False)
    game_session.round_data = data.get('round_data', [])
    game_session.round_results = data.get('round_results', [])
    game_session.is_game_completed = data.get('is_game_completed', False)  # New line
    game_session.save()
    return JsonResponse({'status': 'success'})

from django.utils import timezone

@csrf_exempt
@require_http_methods(["GET"])
def load_game_state(request):
    session_id = request.GET.get('session_id')
    
    try:
        game_session = GameSession.objects.get(session_id=session_id)
        today = timezone.now().date()

        # Check if the game session is for today's date
        if game_session.last_played_date != today:
            # Reset game progress since a new daily game is available
            reset_game_session(game_session)

        return JsonResponse({
            'current_round': game_session.current_round,
            'score': game_session.score,
            'lives_remaining': game_session.lives_remaining,
            'start_player': game_session.start_player,
            'end_player': game_session.end_player,
            'link_type': game_session.link_type,
            'intermediate_players': game_session.intermediate_players,
            'previous_guesses': game_session.previous_guesses,
            'round_scores': game_session.round_scores,
            'is_game_won': game_session.is_game_won,
            'round_data': game_session.round_data,
            'round_results': game_session.round_results,
            'is_game_completed': game_session.is_game_completed  # New line
        })
    except GameSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Game session not found'}, status=404)   

def reset_game_session(game_session):
    """
    Resets the game session for a new daily game.
    """
    game_session.current_round = 0
    game_session.score = 0
    game_session.lives_remaining = 3
    game_session.start_player = ''
    game_session.end_player = ''
    game_session.link_type = ''
    game_session.intermediate_players = []
    game_session.previous_guesses = []
    game_session.round_scores = [0, 0, 0]
    game_session.is_game_won = False
    game_session.round_data = []
    game_session.round_results = ["", "", ""]
    game_session.is_game_completed = False
    game_session.last_played_date = timezone.now().date()
    game_session.save()

def reset_game():
    global player_pairs, current_round
    player_pairs = []
    current_round = 0

def select_unique_players(player_dict):
    global used_players
    
    available_players = [player for player in player_dict.keys()]
    
    if len(available_players) < 2:
        raise ValueError("Not enough unique players available.")
    
    start_player_key = random.choice(available_players)
    end_player_key = random.choice([player for player in available_players if player != start_player_key])

    return start_player_key, end_player_key




from django.db.models import Q

def suggest_player_names(request):
    query = request.GET.get('query', '').strip().lower()
    if not query:
        return JsonResponse([], safe=False)

    # Normalize the query for consistent matching
    normalized_query = normalize_name(query)

    # Efficiently query the database using Q objects for more complex lookups
    # Ensure you have an index on the `normalized_name` field for better performance
    players = Player.objects.filter(
        Q(normalized_name__icontains=normalized_query)
    ).values_list('original_name', flat=True)[:10]  # Use values_list to return only the needed field

    # Prepare club and international team suggestions
    clubs, intl_teams = extract_clubs_and_intl_teams(players)
    club_suggestions = [club for club in clubs if normalized_query in club]
    intl_suggestions = [team for team in intl_teams if normalized_query in team]

    # Combine and limit suggestions to avoid long response times
    combined_suggestions = list(players) + club_suggestions[:5] + intl_suggestions[:5]

    return JsonResponse(combined_suggestions, safe=False)


def normalize_name(name):
    # Normalize the string to ASCII, keep apostrophes, and convert to lowercase
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # Remove all non-alphanumeric characters except apostrophes
    name = re.sub(r"[^\w\s']", '', name)
    # Convert to lowercase and remove spaces
    return name.lower().replace(" ", "")

from asgiref.sync import sync_to_async

async def validate_chain(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start_player = data['start_player']
        end_player = data['end_player']
        intermediate_players = data['intermediate_players']
        link_type = data.get('link_type', 'both')
        allow_multiple_links = data.get('allow_multiple_links', False)

        # Normalize names
        normalized_chain = [normalize_name(start_player)] + [normalize_name(player) for player in intermediate_players] + [normalize_name(end_player)]

        # Load player data efficiently
        player_data = await sync_to_async(load_and_preprocess_player_data)()
        # Validate the player chain
        invalid_links, links, duplicate_clubs, final_chain = validate_player_chain(normalized_chain, player_data, link_type, allow_multiple_links)

        response_data = {
            'valid': len(invalid_links) == 0 and (allow_multiple_links or len(duplicate_clubs) == 0),
            'invalid_links': invalid_links,
            'links': links,
            'duplicate_clubs': duplicate_clubs,
            'final_chain': final_chain
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def compute_common_teams(chain, player_data, link_type):
    """Precompute common clubs and international teams for all player pairs in the chain."""
    common_teams = {}
    for i in range(len(chain) - 1):
        current_player = chain[i]
        next_player = chain[i + 1]

        if current_player not in player_data or next_player not in player_data:
            common_teams[(current_player, next_player)] = ([], [])
            continue

        # Find common clubs and international teams
        common_clubs = find_common_teams(player_data[current_player]['club_career'], player_data[next_player]['club_career'])
        common_intl = find_common_teams(player_data[current_player]['intl_career'], player_data[next_player]['intl_career'])
        common_teams[(current_player, next_player)] = (common_clubs, common_intl)
    
    return common_teams


def validate_player_chain(chain, player_data, link_type, allow_multiple_links):
    invalid_links = []
    links = []
    club_usage = defaultdict(lambda: defaultdict(set))
    final_chain = []
    is_valid_chain = True
    duplicate_clubs = {}

    # Precompute common teams for all player pairs
    common_teams = compute_common_teams(chain, player_data, link_type)

    for i in range(len(chain) - 1):
        current_player = chain[i]
        next_player = chain[i + 1]

        if current_player not in player_data or next_player not in player_data:
            invalid_links.append({
                'from': current_player,
                'to': next_player,
                'reason': 'Player data not found'
            })
            is_valid_chain = False
            continue

        common_clubs, common_intl = common_teams[(current_player, next_player)]

        if link_type == 'club' and not common_clubs:
            invalid_links.append({
                'from': player_data[current_player]['original_name'],
                'to': player_data[next_player]['original_name'],
                'reason': 'No common club teams'
            })
            is_valid_chain = False
        elif link_type == 'both' and not (common_clubs or common_intl):
            invalid_links.append({
                'from': player_data[current_player]['original_name'],
                'to': player_data[next_player]['original_name'],
                'reason': 'No common teams'
            })
            is_valid_chain = False
        else:
            for club in common_clubs:
                club_name = club[1]
                club_usage[club_name][(player_data[current_player]['original_name'], player_data[next_player]['original_name'])].add(club[0])
                #print(f"Club {club_name} links {player_data[current_player]['original_name']} and {player_data[next_player]['original_name']} with seasons {club[0]}")

            if link_type == 'both':
                for intl in common_intl:
                    intl_team = intl[1]
                    club_usage[intl_team][(player_data[current_player]['original_name'], player_data[next_player]['original_name'])].add(intl[0])
                   # print(f"International team {intl_team} links {player_data[current_player]['original_name']} and {player_data[next_player]['original_name']} with seasons {intl[0]}")

            links.append({
                'player': player_data[current_player]['original_name'],
                'next_player': player_data[next_player]['original_name'],
                'common_clubs': [{'season': club[0], 'team': club[1]} for club in common_clubs],
                'common_intl': [{'season': intl[0], 'team': intl[1]} for intl in common_intl] if link_type == 'both' else []
            })

    if is_valid_chain:
        if allow_multiple_links:
            #print("Allow multiple club links is enabled. Skipping duplicate club checks.")
            final_chain = [
                (chain[i], chain[i+1], next(iter(common_teams[(chain[i], chain[i+1])][0] if link_type == 'club' else
                    common_teams[(chain[i], chain[i+1])][0] | common_teams[(chain[i], chain[i+1])][1]), (None, 'No common team found'))[1])
                for i in range(len(chain) - 1)
            ]
        else:
            #print("\n--- Checking for Duplicate Clubs ---")
            for club, player_pairs in club_usage.items():
               # print(f"Club/International Team: {club}, Player Pairs: {player_pairs}")
                if len(player_pairs) > 1:
                    duplicate_clubs[club] = list(player_pairs)
                   # print(f"Duplicate club detected: {club}")

            def explore_chain(current_index, used_clubs, current_chain):
                if current_index >= len(chain) - 1:
                    final_chain.extend(current_chain)
                    return True

                current_player = chain[current_index]
                next_player = chain[current_index + 1]
                common_clubs, common_intl = common_teams[(current_player, next_player)]

                all_possible_links = common_clubs if link_type == 'club' else common_clubs | common_intl

                for club in all_possible_links:
                    club_name = club[1]
                    if club_name in used_clubs:
                        continue

                    used_clubs.add(club_name)
                    current_chain.append((current_player, next_player, club_name))

                    if explore_chain(current_index + 1, used_clubs, current_chain):
                        return True

                    used_clubs.remove(club_name)
                    current_chain.pop()

                return False

            is_valid_chain = explore_chain(0, set(), [])
           
          
    if is_valid_chain:
       # print("\nFinal valid chain:")
        for link in final_chain:
            print(f"{link[0]} to {link[1]} via {link[2]}")
    else:
        print("No valid chain available.")

    return invalid_links, links, duplicate_clubs if not allow_multiple_links else {}, final_chain


def process_career_data(career_data):
    """
    Processes career data into a consistent format for quick lookups.
    Converts each career entry into a tuple of (season, team).
    """
    processed_data = []
    for entry in career_data:
        if len(entry) == 2:
            season, *name_parts = entry[0].split(maxsplit=1)
            name = " ".join(name_parts + [entry[1]]) if name_parts else entry[1]
        else:
            season = "Unknown Season"
            name = " ".join(entry)  # Fallback to combining all parts

        processed_data.append((season, name))
    return processed_data

def find_common_teams(player1_career, player2_career):
    # Use set comprehension to ensure the output is a set
    return {(team1[0], team1[1]) for team1 in player1_career for team2 in player2_career if team1[1] == team2[1] and team1[0] == team2[0]}

def get_last_name(name):
    if not name.strip():
        return ''
    return name.split()[-1]

from django.core.exceptions import ObjectDoesNotExist



def extract_clubs_and_intl_teams(players):
    clubs = set()
    intl_teams = set()
    for player in players:
        try:
            club_career = json.loads(player.club_career)
            intl_career = json.loads(player.intl_career)
            for club in club_career:
                clubs.add(club[1])
            for intl in intl_career:
                intl_teams.add(intl[1])
        except:
            continue
    club_data = {normalize_name(club): club for club in clubs}
    intl_data = {normalize_name(intl): intl for intl in intl_teams}
    return club_data, intl_data
def find_common_teams(player1_career, player2_career):
    return player1_career & player2_career



def load_and_preprocess_player_data():
    """
    Efficiently loads and preprocesses player data for validation.
    Returns a dictionary with normalized player names as keys and their respective data.
    """
    players = Player.objects.all().values('original_name', 'normalized_name', 'club_career', 'intl_career')
    
    player_data = {}

    for player in players:
        try:
            # Attempt to load and preprocess club career data
            club_career = json.loads(player['club_career'])
            processed_club_career = process_career_data(club_career)
            
            # Attempt to load and preprocess international career data
            intl_career = json.loads(player['intl_career'])
            processed_intl_career = process_career_data(intl_career)

            # Normalize the player name for consistent key usage
            normalized_name = normalize_name(player['original_name'])

            # Store the data in a dictionary for fast lookups
            player_data[normalized_name] = {
                'original_name': player['original_name'],
                'club_career': set(processed_club_career),
                'intl_career': set(processed_intl_career)
            }

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors if the data is malformed
            print(f"Error parsing JSON for player {player['original_name']}: {e}")
            continue
        except Exception as e:
            # Catch any other exceptions to avoid breaking the loop
            print(f"Unexpected error processing player {player['original_name']}: {e}")
            continue

    return player_data


def get_player_data(request):
    # Get the player name from the request
    player_name = request.GET.get('player_name', '').strip()
    # Normalize the player name for lookup
    normalized_name = normalize_name(player_name)

    try:
        # Use normalized_name to query the player
        player = Player.objects.get(normalized_name=normalized_name)
        player_data = {
            'original_name': player.original_name,
            'wiki_url': player.wiki_url,
            'full_record': player.full_record,
            'club_career': player.club_career,
            'intl_career': player.intl_career
        }
        return JsonResponse(player_data)
    except Player.DoesNotExist:
        return JsonResponse({'error': 'Player not found'}, status=404)

def generate_player_chain(request):
    try:
        length = int(request.GET.get('length', '').strip())
    except ValueError:
        return JsonResponse({'error': 'Invalid length'}, status=400)

    if length < 2:
        return JsonResponse({'error': 'Length must be at least 2'}, status=400)

    # Load and preprocess player data
    player_data = load_and_preprocess_player_data()
    all_players = list(player_data.keys())

    # Select a random start and end player
    start_player = random.choice(all_players)
    end_player = random.choice(all_players)

    chain = [start_player]

    while len(chain) < length:
        next_player = random.choice(all_players)
        if next_player != chain[-1]:
            chain.append(next_player)

    chain_details = []
    for i in range(len(chain) - 1):
        player = Player.objects.get(normalized_name=chain[i])
        next_player = Player.objects.get(normalized_name=chain[i + 1])
        chain_details.append({
            'player': player.original_name,
            'wiki_url': player.wiki_url,
            'next_player': next_player.original_name,
            'common_clubs': [{'season': club[0], 'team': club[1]} for club in find_common_teams(player_data[player.normalized_name]['club_career'], player_data[next_player.normalized_name]['club_career'])],
            'common_intl': [{'season': intl[0], 'team': intl[1]} for intl in find_common_teams(player_data[player.normalized_name]['intl_career'], player_data[next_player.normalized_name]['intl_career'])]
        })

    return JsonResponse(chain_details, safe=False)

def find_close_matches(query, data, cutoff=0.8):
    """
    Finds close matches for the given query in the provided data.
    """
    normalized_names = list(data.keys())
    last_name = get_last_name(query)
    last_name_matches = [n for n in normalized_names if last_name and last_name in get_last_name(n)]
    last_name_matches_sorted = sorted(last_name_matches, key=lambda x: difflib.SequenceMatcher(None, query, x).ratio(), reverse=True)
    matches = last_name_matches_sorted[:5]
    if len(matches) < 5:
        additional_matches = difflib.get_close_matches(query, normalized_names, n=5-len(matches), cutoff=cutoff)
        matches.extend([m for m in additional_matches if m not in matches])
    return matches



def extract_career_range(player_data, player_name):
    """Extract the career range for a player from their club and international records."""
    try:
        club_career = list(player_data.get('club_career', []))  # Ensure club_career is a list
        intl_career = list(player_data.get('intl_career', []))  # Ensure intl_career is a list
        all_seasons = set()

        for record in club_career + intl_career:
            if len(record) >= 2:
                # Normalize and clean season strings
                season_str = re.sub(r'\D', '', record[0].split('-')[0])  # Keep only digits
                try:
                    
                    if season_str:
                        season = int(season_str)
                        all_seasons.add(season)
                    else:
                        print(f"Warning: Unable to parse season '{record[0]}' for player {player_name}")
                except ValueError:
                    print(f"Warning: Unable to parse season '{record[0]}' for player {player_name}")

        if all_seasons:
            return min(all_seasons), max(all_seasons)
    except Exception as e:
        print(f"Error extracting career range for player {player_name}: {e}")
        print(f"Career Overview for player {player_name}: Club - {club_career}, International - {intl_career}")
    return None, None

def filter_players_by_career_range(player_data, start_player, end_player):
    """Filter players by career range overlap."""
    start_min, start_max = extract_career_range(player_data[start_player], start_player)
    end_min, end_max = extract_career_range(player_data[end_player], end_player)
    
    if start_min is None or end_min is None:
        return player_data  # Return original if any career range extraction fails
    
    filtered_player_data = {}
    for player, data in player_data.items():
        player_min, player_max = extract_career_range(data, player)
        if player_min is None:
            continue
        
        if (player_max >= start_min and player_min <= start_max) or (player_max >= end_min and player_min <= end_max):
            filtered_player_data[player] = data
    
    return filtered_player_data

def find_link(request):
    start_player = request.GET.get('start_player', '').strip()
    end_player = request.GET.get('end_player', '').strip()
    link_type = request.GET.get('link_type', 'both')

    if not start_player or not end_player:
        return JsonResponse({'error': 'Both player fields are required.'}, status=400)

    normalized_start_player = normalize_name(start_player)
    normalized_end_player = normalize_name(end_player)
    cache_key = f"find_link_{normalized_start_player}_{normalized_end_player}_{link_type}"

    # Check if the result is in the cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return JsonResponse(cached_result, safe=False)

    player_data = load_and_preprocess_player_data()
    filtered_player_data = filter_players_by_career_range(player_data, normalized_start_player, normalized_end_player)

    start_time = time.time()
    try:
        shortest_link = bfs_bidirectional(filtered_player_data, normalized_start_player, normalized_end_player, link_type)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    end_time = time.time()

    if shortest_link:
        if shortest_link[-1] == normalize_name(start_player):
            shortest_link.reverse()

        link_details = []
        for i in range(len(shortest_link) - 1):
            try:
                player = Player.objects.get(normalized_name=shortest_link[i])
                next_player = Player.objects.get(normalized_name=shortest_link[i + 1])
            except Player.DoesNotExist:
                continue

            common_clubs = find_common_teams(player_data[player.normalized_name]['club_career'], player_data[next_player.normalized_name]['club_career'])
            common_intl = find_common_teams(player_data[player.normalized_name]['intl_career'], player_data[next_player.normalized_name]['intl_career'])

            formatted_common_clubs = [{'season': club[0], 'team': club[1]} for club in common_clubs]
            formatted_common_intl = [{'season': intl[0], 'team': intl[1]} for intl in common_intl]

            link_details.append({
                'player': player.original_name,
                'wiki_url': player.wiki_url,
                'next_player': next_player.original_name,
                'common_clubs': formatted_common_clubs,
                'common_intl': formatted_common_intl if link_type != 'club' else []
            })

        response_data = {'link_details': link_details, 'is_optimal': True}
    else:
        response_data = {'link_details': None, 'is_optimal': False}

    # Store the result in the cache for one week
    cache.set(cache_key, response_data, timeout=60*60*24*7)  # Cache for 7 days
    return JsonResponse(response_data, safe=False)









def bfs_bidirectional(player_data, start_player, end_player, link_type):
    # Initialization of BFS queues and visited sets for both directions
    queue_start = [(start_player, [start_player])]
    queue_end = [(end_player, [end_player])]
    visited_start = {start_player: [start_player]}
    visited_end = {end_player: [end_player]}

    while queue_start and queue_end:
        # Expand the search from the start side
        if queue_start:
            current_player, path = queue_start.pop(0)
            for neighbor in get_neighbors(current_player, player_data, link_type):
                if neighbor not in visited_start:
                    new_path = path + [neighbor]
                    visited_start[neighbor] = new_path
                    queue_start.append((neighbor, new_path))

                    if neighbor in visited_end:
                        return new_path + visited_end[neighbor][::-1][1:]  # Join the two paths

        # Expand the search from the end side
        if queue_end:
            current_player, path = queue_end.pop(0)
            for neighbor in get_neighbors(current_player, player_data, link_type):
                if neighbor not in visited_end:
                    new_path = path + [neighbor]
                    visited_end[neighbor] = new_path
                    queue_end.append((neighbor, new_path))

                    if neighbor in visited_start:
                        return visited_start[neighbor] + new_path[::-1][1:]  # Join the two paths

    return None

def get_neighbors(current_player, player_data, link_type):
    neighbors = []
    for neighbor, data in player_data.items():
        if neighbor == current_player:
            continue
        common_clubs = find_common_teams(player_data[current_player]['club_career'], data['club_career'])
        common_intl = find_common_teams(player_data[current_player]['intl_career'], data['intl_career'])

        if (link_type == 'club' and common_clubs) or (link_type == 'both' and (common_clubs or common_intl)):
            neighbors.append(neighbor)
    return neighbors




def player_overview(request):
    # Get the normalized names of start and end players from the request
    start_player = request.GET.get('start_player', '').strip()
    end_player = request.GET.get('end_player', '').strip()
    link_type = request.GET.get('link_type', 'club').strip().lower()

    # Normalize the names using the same function used for normalization elsewhere in the code
    normalized_start_player = normalize_name(start_player)
    normalized_end_player = normalize_name(end_player)

    # Retrieve player data using normalized names
    start_player_data = Player.objects.filter(normalized_name=normalized_start_player).first()
    end_player_data = Player.objects.filter(normalized_name=normalized_end_player).first()

    print(start_player_data)
    print(end_player_data)
    if not start_player_data or not end_player_data:
        return JsonResponse({'error': 'Player data not found'}, status=404)

    response_data = {}

    if link_type == 'both':
        response_data['start_player_club_overview'] = generate_career_overview(start_player_data, 'club')
        response_data['start_player_intl_overview'] = generate_career_overview(start_player_data, 'international')
        response_data['end_player_club_overview'] = generate_career_overview(end_player_data, 'club')
        response_data['end_player_intl_overview'] = generate_career_overview(end_player_data, 'international')
    else:
        if link_type == 'club':
            response_data['start_player_club_overview'] = generate_career_overview(start_player_data, link_type)
            response_data['end_player_club_overview'] = generate_career_overview(end_player_data, link_type)
        elif link_type == 'international':
            response_data['start_player_intl_overview'] = generate_career_overview(start_player_data, link_type)
            response_data['end_player_intl_overview'] = generate_career_overview(end_player_data, link_type)

    return JsonResponse(response_data)




















def find_optimal_links(request):
    start_player = request.GET.get('start_player', '').strip()
    end_player = request.GET.get('end_player', '').strip()
    link_type = request.GET.get('link_type', 'both')

    if not start_player or not end_player:
        return JsonResponse({'error': 'Both player fields are required.'}, status=400)

    normalized_start_player = normalize_name(start_player)
    normalized_end_player = normalize_name(end_player)

    player_data = load_and_preprocess_player_data()

    optimal_path = bfs_bidirectional(player_data, normalized_start_player, normalized_end_player, link_type)

    if optimal_path:
        optimal_links = []
        for i in range(len(optimal_path) - 1):
            player = Player.objects.get(normalized_name=optimal_path[i])
            next_player = Player.objects.get(normalized_name=optimal_path[i + 1])

            common_clubs = find_common_teams(player_data[player.normalized_name]['club_career'], player_data[next_player.normalized_name]['club_career'])
            common_intl = find_common_teams(player_data[player.normalized_name]['intl_career'], player_data[next_player.normalized_name]['intl_career'])

            optimal_links.append({
                'player': player.original_name,
                'next_player': next_player.original_name,
                'wiki_url': player.wiki_url,
                'common_clubs': [{'season': club[0], 'team': club[1]} for club in common_clubs],
                'common_intl': [{'season': intl[0], 'team': intl[1]} for intl in common_intl] if link_type != 'club' else []
            })
        return JsonResponse(optimal_links, safe=False)
    else:
        return JsonResponse({'error': 'No optimal path found'}, status=404)


def consolidate_seasons(data):
    consolidated = []
    data.sort(key=lambda x: x['season'])  # Sort data by season

    current_team = data[0]['team']
    start_season = data[0]['season'][:4]
    end_season = data[0]['season'][5:]

    for i in range(1, len(data)):
        season, team = data[i]['season'], data[i]['team']
        if team == current_team:
            end_season = season[5:]
        else:
            consolidated.append({'season': f'{start_season}-{end_season}', 'team': current_team})
            current_team = team
            start_season = season[:4]
            end_season = season[5:]

    consolidated.append({'season': f'{start_season}-{end_season}', 'team': current_team})

    return consolidated




def generate_career_overview(player, link_type):
    try:
        club_career = json.loads(player.club_career)
        intl_career = json.loads(player.intl_career)
        
        overview = []
        if link_type == 'club':
            for club in club_career:
                if len(club) == 2:
                    season, *club_name_parts = club[0].split(maxsplit=1)
                    club_name = " ".join(club_name_parts + [club[1]]) if club_name_parts else club[1]
                else:
                    season = "Unknown Season"
                    club_name = " ".join(club)
                overview.append({'season': season, 'team': club_name})

        if link_type == 'international':
            for intl in intl_career:
                if len(intl) == 2:
                    season, *team_name_parts = intl[0].split(maxsplit=1)
                    team_name = " ".join(team_name_parts + [intl[1]]) if team_name_parts else intl[1]
                else:
                    season = "Unknown Season"
                    team_name = " ".join(intl)
                overview.append({'season': season, 'team': team_name})
     
        overview = consolidate_seasons(overview)
        #print(overview)
        return overview
    except Exception as e:
        print(f"Error generating career overview for player {player.original_name}: {e}")
        return []

from django.http import JsonResponse
from django.utils import timezone
from .models import DailyGame

def get_precomputed_optimal_links(request):
    start_player = request.GET.get('start_player', '').strip()
    end_player = request.GET.get('end_player', '').strip()

    if not start_player or not end_player:
        return JsonResponse({'error': 'Both player fields are required.'}, status=400)

    today = timezone.now().date()

    try:
        # Retrieve the precomputed game for today
        daily_game = DailyGame.objects.get(date=today)
        
        # Find the correct link between the start and end player
        for i, (start, end) in enumerate(daily_game.player_pairs):
            if start == start_player and end == end_player:
                precomputed_links = daily_game.precomputed_links[i]
                return JsonResponse(precomputed_links, safe=False)

        return JsonResponse({'error': 'No precomputed optimal links found for the given players.'}, status=404)

    except DailyGame.DoesNotExist:
        return JsonResponse({'error': 'Daily game data not found for today.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
