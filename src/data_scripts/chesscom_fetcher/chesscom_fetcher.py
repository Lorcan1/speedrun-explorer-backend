import csv
import json
from collections import Counter

from src.data_scripts.chesscom_fetcher.chesscom_data_loader import chesscom_loader
from chessdotcom import ChessDotComClient

client = ChessDotComClient(user_agent="My Python Application...")


total_games = []

# months = [(2020, 10), (2020, 11), (2020, 12), (2021, 1), (2021, 2)]
months = [(2024, 2), (2024, 3), (2024, 4), (2024, 5), (2024, 6), (2024, 7), (2024, 8), (2024, 9), (2024, 10),(2024, 11),(2024, 12),(2025, 1),
          (2025, 2), (2025, 3), (2025, 4), (2025, 5), (2025, 6), (2025, 7), (2025, 8), (2025, 9), (2025, 10)]

for y, m in months:
    response = client.get_player_games_by_month(username="HebeccaRaris", year=y, month=m)

    total_games.extend(response.json["games"])

print(len(total_games))

youtuber_username = "HebeccaRaris"

opponents = set()
opps_list = []
for game in total_games:
    white = game["white"]["username"]
    black = game["black"]["username"]
    opponent = black if white.lower() == youtuber_username.lower() else white
    opponents.add(opponent)
    opps_list.append(opponent)

opponent_list = sorted(opponents, key=str.lower)

print(len(opponent_list))

with open("opponents.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Opponent"])
    for name in opponent_list:
        writer.writerow([name])

chesscom_loader(total_games)


counts = Counter(opps_list)

duplicates = {value: count for value, count in counts.items() if count > 1}
print(duplicates)


with open("duplicates.json", "w") as f:
    json.dump(duplicates, f, indent=2)
