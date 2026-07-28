import chess.pgn
import re

# YouTube: matches youtu.be/ID or youtube.com/watch?v=ID, with optional timestamp
youtube_pattern = re.compile(
    r"https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)[\w-]+(?:[?&]t=\d+)?"
)

# Chess.com: matches chess.com/live/game/ID or chess.com/game/live/ID
chesscom_pattern = re.compile(
    r'(?:https?://)?(?:www\.)?chess\.com/(?:live/game|game/live)/\d+'
)

output = []

with open(
    "lichess_study\lichess_study_sensei-danya-speedrun-part-2_by_rudisco_2021.03.14.pgn"
) as pgn_file:
    while True:
        game_json = {}
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break

        # print(f"Chapter/Event {game.headers['Event']}")
        try:
            # print(game.headers)

            game_json["chapter_name"] = game.headers["ChapterName"]
            game_json["study_name"] = game.headers["StudyName"]
            game_json["chapter_url"] = game.headers["ChapterURL"]
            game_json["white"] = game.headers["White"]
            game_json["black"] = game.headers["Black"]
            game_json["result"] = game.headers["Result"]
            game_json["white_elo"] = game.headers["WhiteElo"]
            game_json["black_elo"] = game.headers["BlackElo"]
            game_json["date"] = game.headers["Date"]
            game_json["eco"] = game.headers["ECO"]
            game_json["opening"] = game.headers["Opening"]
            game_json["time_control"] = game.headers["TimeControl"]
            game_json["termination"] = game.headers["Termination"]

            comment_text = game.comment
            youtube_match = youtube_pattern.search(comment_text)
            chess_com_match = chesscom_pattern.search(comment_text)

            youtube_url = youtube_match.group(0) if youtube_match else None
            chesscom_url = chess_com_match.group(0) if chess_com_match else None

            game_json["youtube_url"]  = youtube_url
            game_json["youtube_found"] = bool(youtube_match)
            game_json["chesscom_url"] = chesscom_url
            game_json["chesscom_found"] = bool(chess_com_match)
            # game_json["pgn_moves"]
            #
            print(game_json)
            output.append(game_json)

        except Exception as e:
            print(e)

print(output)
