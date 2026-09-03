import csv
import json
from collections import Counter

from data_scripts.chesscom_fetcher.chesscom_data_loader import chesscom_loader
from chessdotcom import ChessDotComClient

client = ChessDotComClient(user_agent="My Python Application...")


total_games = []

# months = [(2020, 10), (2020, 11), (2020, 12), (2021, 1), (2021, 2)]
months = [(2021, 12), (2022, 1), (2022, 2), (2022, 3), (2022, 4), (2022, 5), (2022, 6), (2022, 7), (2022, 8), (2022, 9), (2022, 10) ]

for y, m in months:
    response = client.get_player_games_by_month(username="SenseiDanya", year=y, month=m)

    total_games.extend(response.json["games"])

print(len(total_games))

youtuber_username = "SenseiDanya"

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

# with open("opponents.csv", "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow(["Opponent"])
#     for name in opponent_list:
#         writer.writerow([name])

# chesscom_loader(total_games)


counts = Counter(opps_list)

duplicates = {value: count for value, count in counts.items() if count > 1}
print(duplicates)


# with open("duplicates.json", "w") as f:
#     json.dump(duplicates, f, indent=2)
