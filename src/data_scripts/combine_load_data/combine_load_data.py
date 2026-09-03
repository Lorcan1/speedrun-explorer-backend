import pandas as pd
import json
import csv
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import logging
from collections import Counter


logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

df = pd.read_csv("Speedrun Video Opp Matcher - Sheet1.csv")
df.head()  # first 5 rows
print(df.columns)  # list of column names (the "titles")

with open("youtube_videos.json", "r") as f:
    videos = json.load(f)
    print(videos[:3])

with open("games.json", "r") as f:
    games = json.load(f)
    print(games[:3])

with open("duplicates.json", "r") as f:
    duplicates = json.load(f)


videos_lookup = {}
videos_duplicates_lookup = {}


def add_timestamp(url, hours=0, minutes=0, seconds=0):
    total_seconds = hours * 3600 + minutes * 60 + seconds

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["t"] = [f"{total_seconds}s"]

    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


csv_opponents = []
with open("Speedrun Video Opp Matcher - Sheet1.csv", newline="") as f:
    reader = csv.DictReader(f)  # automatically uses row 1 as keys
    for row in reader:
        if row["Opponent Name"] not in duplicates:
            videos_lookup[row["Opponent Name"]] = add_timestamp(
                videos[int(row["Video No"]) - 1]["video_url"],
                hours=int(row["Time Hours"]),
                minutes=int(row["Minutes"]),
                seconds=int(row["Seconds"]),
            )
        elif row["Opponent Name"] in duplicates:
            videos_duplicates_lookup[(row["Opponent Name"], row["ELO"])] = (
                add_timestamp(
                    videos[int(row["Video No"]) - 1]["video_url"],
                    hours=int(row["Time Hours"]),
                    minutes=int(row["Minutes"]),
                    seconds=int(row["Seconds"]),
                )
            )
        csv_opponents.append(row["Opponent Name"])


# i need to get the video url form

updated_games = []
opponents_list = []


for game in games:
    if game["white"] == "SenseiDanya":
        opponent = game["black"]
        danya_elo = str(game["white_elo"])
    elif game["black"] == "SenseiDanya":
        opponent = game["white"]
        danya_elo = str(game["black_elo"])
    else:
        logging.error(f"No video found for opponent: {opponent}")
        continue

    if opponent not in duplicates:
        if opponent in videos_lookup:
            game["youtube_url"] = videos_lookup[opponent]
            game["youtube_found"] = True
            updated_games.append(game)
            opponents_list.append(opponent)
        else:
            logging.error(f"No video found for opponent: {opponent}")

    elif opponent in duplicates:
        if (opponent, danya_elo) in videos_duplicates_lookup:
            game["youtube_url"] = videos_duplicates_lookup[(opponent, danya_elo)]
            updated_games.append(game)
            opponents_list.append(opponent)
        else:
            logging.error(f"No video found for duplicate opponent/elo: {opponent}")
            continue

print(len(updated_games))


with open("updated_opponents.json", "w") as f:
    json.dump(opponents_list, f, indent=2)


# Now compare count of oppoents in updated oppnents vs csv oppenents


c_csv = Counter(csv_opponents)
c_list = Counter(opponents_list)

only_in_csv = (
    c_csv - c_list
)  # in csv_opponents but not (enough times) in opponents_list
only_in_list = (
    c_list - c_csv
)  # in opponents_list but not (enough times) in csv_opponents

print(
    f"len(csv_opponents)={len(csv_opponents)}, len(opponents_list)={len(opponents_list)}"
)
print(f"unique in csv_opponents: {len(c_csv)}, unique in opponents_list: {len(c_list)}")

print("\nOnly in csv_opponents (or extra copies):")
for item, count in only_in_csv.items():
    print(f"  {item!r} x{count}")

print("\nOnly in opponents_list (or extra copies):")
for item, count in only_in_list.items():
    print(f"  {item!r} x{count}")


def dup_summary(name, lst, counter):
    dups = {item: count for item, count in counter.items() if count > 1}
    extra_copies = sum(count - 1 for count in dups.values())
    print(
        f"{name}: {len(lst)} total, {len(counter)} unique, "
        f"{len(dups)} items duplicated, {extra_copies} extra copies"
    )
    if dups:
        for item, count in dups.items():
            print(f"    {item!r} x{count}")


print(
    f"len(csv_opponents)={len(csv_opponents)}, len(opponents_list)={len(opponents_list)}"
)
print(
    f"unique in csv_opponents: {len(c_csv)}, unique in opponents_list: {len(c_list)}\n"
)

dup_summary("csv_opponents", csv_opponents, c_csv)
print()
dup_summary("opponents_list", opponents_list, c_list)

# Example

with open("updated_games.json", "w") as f:
    json.dump(updated_games, f, indent=2)
