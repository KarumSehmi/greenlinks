import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def clean_text(text):
    """Remove square bracketed numbers and arrows ("→") from text."""
    return re.sub(r'\[\d+\]|→', '', text).strip()

def is_valid_year(year):
    """Check if the given year string can be converted to a valid integer."""
    try:
        int(year)
        return True
    except ValueError:
        return False

def expand_years_to_seasons(years, default_start_year=None, name=None):
    """Expand a range of years into individual seasons."""
    try:
        seasons = []
        years = years.replace('–', '-').strip()
        if '?' in years:
            return []  # Skip invalid year entries with a question mark
        if '-' in years:
            start_year, end_year = years.split('-')
            start_year = start_year.strip()
            end_year = end_year.strip()

            if not is_valid_year(start_year) or int(start_year) < 1900:
                if is_valid_year(end_year):
                    start_year = str(int(end_year) - 1)
                elif default_start_year is not None:
                    start_year = default_start_year
                else:
                    return []  # Skip invalid year entries
            start_year = int(start_year)

            if not is_valid_year(end_year) or end_year == "":
                if int(start_year) > 2000:
                    end_year = datetime.now().year + 1
                else:
                    end_year = str(int(start_year) + 2)

            start_year = int(start_year)
            end_year = int(end_year)

            for year in range(start_year, end_year):
                season = f"{year}/{year + 1}"
                seasons.append(season)
        else:
            if is_valid_year(years):
                year = int(years)
                seasons.append(f"{year}/{year + 1}")
        return seasons
    except:
        save_failed_season(name, years, r'D:\CHAIN\playerscraper\createdatabase\failed_seasons.txt')

def get_player_links_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    player_links = []

    div = soup.find('div', {'id': 'mw-pages'})
    if div:
        for li in div.find_all('li'):
            link = li.find('a', href=True)
            if link:
                player_name = link.text
                player_name = re.sub(r'\s*\(.*?\)\s*', '', player_name)  # Remove any text within brackets
                player_url = 'https://en.wikipedia.org' + link['href']
                player_links.append((player_name, player_url))

    return player_links

def get_all_player_links(base_urls):
    all_player_links = []
    for base_url in base_urls:
        url = base_url
        while url:
            print(f"Scraping {url}")
            player_links = get_player_links_from_page(url)
            all_player_links.extend(player_links)

            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            next_link = soup.find('a', string='next page')


            if next_link:
                url = 'https://en.wikipedia.org' + next_link['href']
            else:
                url = None

    return all_player_links

def save_to_file(player_links, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for name, link in player_links:
            file.write(f"{name}: {link}\n")

def fetch_player_career_stats(player_url, failed_seasons_file, player_name):
    response = requests.get(player_url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        infobox = soup.find('table', {'class': 'infobox vcard'})
        
        if not infobox:
            infobox = soup.find('table', {'class': 'infobox biography vcard'})
        
        if not infobox:
            infobox = soup.find('table', {'class': 'infobox'})

        # Initialize data holders
        personal_info = {}
        youth_career_data = []
        senior_career_data = []
        international_career_data = []
        managerial_career_data = []

        if infobox:
            rows = infobox.find_all('tr')
            current_section = None
            default_start_year = None
            for row in rows:
                header = row.find('th')
                if header:
                    header_text = clean_text(header.text.strip())
                    if header_text in ['Full name', 'Date of birth', 'Place of birth', 'Height', 'Position(s)']:
                        data = row.find('td')
                        if data:
                            value = clean_text(data.text.strip())
                            personal_info[header_text] = value.lower()

                # Section identification
                if 'Youth career' in row.text:
                    current_section = 'youth'
                    continue
                if 'Senior career' in row.text:
                    current_section = 'senior'
                    continue
                if 'International career' in row.text:
                    current_section = 'international'
                    continue
                if 'Managerial career' in row.text:
                    current_section = 'managerial'
                    continue

                # Data extraction based on section
                th = row.find('th')
                if th and th.get('scope') == 'row':
                    cells = row.find_all('td')
                    if current_section == 'youth' and len(cells) >= 1:
                        years = clean_text(th.text.strip())
                        team = clean_text(cells[0].text.strip())
                        default_start_year = '2008'  # Default for missing start years
                        seasons = expand_years_to_seasons(years, default_start_year, player_name)
                        if not seasons:
                            save_failed_season(player_name, years, failed_seasons_file)
                        for season in seasons:
                            youth_career_data.append((season, team))
                    elif current_section == 'senior' and len(cells) >= 2:
                        years = clean_text(th.text.strip())
                        team = clean_text(cells[0].text.strip())
                        if 'loan' in cells[0].text.lower():
                            team = f"{team}"
                        seasons = expand_years_to_seasons(years)
                        if not seasons:
                            save_failed_season(player_name, years, failed_seasons_file)
                        for season in seasons:
                            senior_career_data.append((season, team))
                    elif current_section == 'international' and len(cells) >= 1:
                        years = clean_text(th.text.strip())
                        team = clean_text(cells[0].text.strip())
                        seasons = expand_years_to_seasons(years)
                        if not seasons:
                            save_failed_season(player_name, years, failed_seasons_file)
                        for season in seasons:
                            international_career_data.append((season, team))
                    elif current_section == 'managerial' and len(cells) >= 1:
                        years = clean_text(th.text.strip())
                        team = clean_text(cells[0].text.strip())
                        seasons = expand_years_to_seasons(years)
                        if not seasons:
                            save_failed_season(player_name, years, failed_seasons_file)
                        for season in seasons:
                            managerial_career_data.append((season, team))

        return personal_info, youth_career_data, senior_career_data, international_career_data, managerial_career_data
    else:
        print(f"Failed to fetch the Wikipedia page for {player_url}")
    return None, None, None, None, None

def save_failed_season(player_name, season, filename):
    if season != "Years":
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f"Player: {player_name}, Season: {season}\n")

def save_data(player_name, player_url, personal_info, youth_career_data, senior_career_data, international_career_data, managerial_career_data, filename):
    data_lines = []

    # Collect all data into lines
    data_lines.append(f"Player Name: {player_name}\n")
    data_lines.append(f"Wikipedia URL: {player_url}\n")
    data_lines.append("Personal Information\n")
    for key, value in personal_info.items():
        data_lines.append(f"{key}: {value}\n")
    data_lines.append("Youth Career\n")
    for entry in youth_career_data:
        data_lines.append(f"{entry[0]}: {entry[1]}\n")
    data_lines.append("Senior Career\n")
    for entry in senior_career_data:
        data_lines.append(f"{entry[0]}: {entry[1]}\n")
    data_lines.append("International Career\n")
    for entry in international_career_data:
        data_lines.append(f"{entry[0]}: {entry[1]}\n")
    data_lines.append("Managerial Career\n")
    for entry in managerial_career_data:
        data_lines.append(f"{entry[0]}: {entry[1]}\n")
    
    # Check the length of data before saving
    if len(data_lines) > 120:
        print(f"Skipping saving data for {player_name} due to excessive length.")
        save_failed_player(player_name, filename.replace('managers_stats.txt', 'failed_players.txt'))
        return

    # Save to file if data length is acceptable
    with open(filename, 'a', encoding='utf-8') as file:
        file.writelines(data_lines)
        file.write("\n")

def save_failed_player(player_name, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"{player_name}\n")

def read_player_links(filename):
    player_links = []
    failed_players_file = filename.replace('prem_players.txt', 'failed_players.txt')  # Derive the failed players file path

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                name, url = line.strip().split(': ', 1)  # Split only at the first occurrence of ': '
                player_links.append((name, url))
            except ValueError:
                print(f"Skipping malformed line: {line.strip()}")
                save_failed_player(line.strip(), failed_players_file)  # Save malformed lines to the failed players file

    return player_links


def load_processed_urls(filename):
    """Load the set of processed player URLs."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        return set()

def save_checkpoint(player_url, checkpoint_file):
    with open(checkpoint_file, 'a', encoding='utf-8') as file:
        file.write(f"{player_url}\n")

from tqdm import tqdm
import time  # Import time to simulate delays for demonstration purposes

def main():
    # List of base URLs to scrape
    base_urls = [
        'https://en.wikipedia.org/wiki/Category:UEFA_Champions_League_winning_players',
        'https://en.wikipedia.org/wiki/Category:Premier_League_players',
        'https://en.wikipedia.org/wiki/Category:La_Liga_players',
        'https://en.wikipedia.org/wiki/Category:Bundesliga_players',
        'https://en.wikipedia.org/wiki/Category:Ligue_1_players', 
        'https://en.wikipedia.org/wiki/Category:Serie_A_players',
    ]
    
    player_links_file = r'D:\CHAIN\playerscraper\createdatabase\prem_players.txt'
    output_file = r'D:\CHAIN\playerscraper\createdatabase\managers_stats.txt'
    checkpoint_file = r'D:\CHAIN\playerscraper\createdatabase\processed_players.txt'
    failed_players_file = r'D:\CHAIN\playerscraper\createdatabase\failed_players.txt'
    failed_seasons_file = r'D:\CHAIN\playerscraper\createdatabase\failed_seasons.txt'
    
    # Step 1: Scrape all player links from multiple URLs and save them
    all_player_links = get_all_player_links(base_urls)
    save_to_file(all_player_links, player_links_file)

    # Step 2: Read player links and fetch their career stats
    player_links = read_player_links(player_links_file)
    processed_urls = load_processed_urls(checkpoint_file)

    # Step 3: Process each player with a progress bar
    for player_name, player_url in tqdm(player_links, desc="Processing Players", unit="player"):
        try:
            if player_url in processed_urls:
                print(f"Skipping {player_name} ({player_url}), already processed.")
                continue
        
            print(f"Fetching profile for {player_name}...")
            personal_info, youth_career_data, senior_career_data, international_career_data, managerial_career_data = fetch_player_career_stats(player_url, failed_seasons_file, player_name)
        
            if personal_info or youth_career_data or senior_career_data or international_career_data or managerial_career_data:
                print(f"Saving stats for {player_name}")
                save_data(player_name, player_url, personal_info, youth_career_data, senior_career_data, international_career_data, managerial_career_data, output_file)
                save_checkpoint(player_url, checkpoint_file)
            else:
                print(f"Could not fetch career stats for {player_name}. Adding to failed players list.")
                save_failed_player(player_name, failed_players_file)
        except Exception as e:
            print(f"Error processing {player_name}: {e}")
            save_failed_player(player_name, failed_players_file)

if __name__ == "__main__":
    main()

