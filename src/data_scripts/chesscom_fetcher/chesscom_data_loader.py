import io
import json
import os

import chess.pgn


def chesscom_loader(total_games):
    games = []

    for game_data in total_games:
        game_json = {}
        try:
            pgn_text = game_data.get("pgn", "")
            game = chess.pgn.read_game(io.StringIO(pgn_text))
            if game is None:
                continue

            headers = game.headers

            game_json["game_id"] = str(game_data.get("url", "").rstrip("/").split("/")[-1])
            game_json["chapter_name"] = None   # not applicable — chess.com source, not lichess study
            game_json["study_name"] = None     # not applicable — chess.com source, not lichess study
            game_json["chapter_url"] = None    # not applicable — chess.com source, not lichess study
            game_json["white"] = headers.get("White")
            game_json["black"] = headers.get("Black")
            game_json["result"] = headers.get("Result")
            game_json["white_elo"] = headers.get("WhiteElo")
            game_json["black_elo"] = headers.get("BlackElo")
            game_json["date"] = headers.get("Date")
            game_json["eco"] = headers.get("ECO")
            game_json["opening"] = headers.get("Opening") or headers.get("ECOUrl")
            game_json["time_control"] = headers.get("TimeControl")
            game_json["termination"] = headers.get("Termination")
            game_json["youtube_url"] = None    # to be filled in manually later
            game_json["youtube_found"] = False # to be filled in manually later
            game_json["chesscom_url"] = game_data.get("url")
            game_json["chesscom_found"] = True

            exporter = chess.pgn.StringExporter(
                headers=False, variations=False, comments=False
            )
            moves_only_pgn = game.accept(exporter)

            game_json["pgn_moves"] = moves_only_pgn

            games.append(game_json)

        except Exception as e:
            print(f"Error: {e}")

    print(len(games))

    existing = []
    if os.path.exists("games.json"):
        with open("games.json") as f:
            existing = json.load(f)

    existing.extend(games)

    with open("games.json", "w") as f:
        json.dump(existing, f, indent=2)