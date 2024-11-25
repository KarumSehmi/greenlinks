

import re

# Function to extract player records based on Wikipedia URL
def extract_player_records(merged_content):
    pattern = r"(Player Name: .+?)(?=Player Name: |$)"
    return re.findall(pattern, merged_content, re.DOTALL)

# Function to extract the Wikipedia URL from a player record
def extract_wikipedia_url(player_record):
    pattern = r"Wikipedia URL: (.+)"
    match = re.search(pattern, player_record)
    return match.group(1) if match else None

# Path to the merged player statistics document
merged_file_path = r"D:\CHAIN\playerscraper\createdatabase\managers_stats.txt"
new_file_path = r"D:\CHAIN\unique_player_stats.txt"

# Read the merged content from the file
with open(merged_file_path, 'r', encoding='utf-8') as file:
    merged_content = file.read()

# Extract player records and remove duplicates based on Wikipedia URL
player_records = extract_player_records(merged_content)
unique_records = {}
for record in player_records:
    url = extract_wikipedia_url(record)
    if url and url not in unique_records:
        unique_records[url] = record

# Write the unique player records to a new file
with open(new_file_path, 'w', encoding='utf-8') as output:
    for record in unique_records.values():
        output.write(record + "\n")

print(f"Unique player records written to {new_file_path}")
