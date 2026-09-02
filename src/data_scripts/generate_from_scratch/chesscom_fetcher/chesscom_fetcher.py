import csv

from chesscom_data_loader import chesscom_loader
from chessdotcom import ChessDotComClient

client = ChessDotComClient(user_agent="My Python Application...")


total_games = []

months = [(2020, 10), (2020, 11), (2020, 12), (2021, 1), (2021, 2)]

for y, m in months:
    response = client.get_player_games_by_month(username="SenseiDanya", year=y, month=m)

    total_games.extend(response.json["games"])

print(len(total_games))

youtuber_username = "SenseiDanya"

opponents = set()
for game in total_games:
    white = game["white"]["username"]
    black = game["black"]["username"]
    opponent = black if white.lower() == youtuber_username.lower() else white
    opponents.add(opponent)

opponent_list = sorted(opponents, key=str.lower)

print(len(opponent_list))

with open("opponents.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Opponent"])
    for name in opponent_list:
        writer.writerow([name])

chesscom_loader(total_games)
