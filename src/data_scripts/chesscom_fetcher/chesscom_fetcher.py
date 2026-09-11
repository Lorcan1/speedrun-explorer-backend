import csv
import json
from collections import Counter

from src.data_scripts.chesscom_fetcher.chesscom_data_loader import chesscom_loader
from chessdotcom import ChessDotComClient

client = ChessDotComClient(user_agent="My Python Application...")

speedrunner_username = "OhMyLands"


total_games = []

# months = [(2020, 10), (2020, 11), (2020, 12), (2021, 1), (2021, 2)]
months = [(2021, 3), (2021, 4), (2021, 5), (2021, 6), 
          (2021, 7), (2021, 8), (2021, 9), (2021, 10)]

for y, m in months:
    response = client.get_player_games_by_month(username=speedrunner_username, year=y, month=m)

    total_games.extend(response.json["games"])

print(len(total_games))



opponents = set()
opps_list = []
for game in total_games:
    white = game["white"]["username"]
    black = game["black"]["username"]
    opponent = black if white.lower() == speedrunner_username.lower() else white
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
