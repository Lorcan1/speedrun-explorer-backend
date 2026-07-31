import io
import json

import chess.pgn

from src.utils.fen_trimmer import fen_trimmer

with open('data/games.json') as f:
    games = json.load(f)

fen = []

for game_json in games: 
    game = chess.pgn.read_game(io.StringIO(game_json["pgn_moves"]))
    board = game.board()
    
    ply = 0
    san = None
    for move in game.mainline_moves():
        move_json = {}
        move_json["game_id"] = game_json["game_id"]
        move_json["ply"] = ply
        move_json["move_number"] = 0 if not ply else (ply + 1) // 2
        move_json["san"] = san
        move_json["side_to_move_next"] = "white" if board.turn else "black"
        move_json["fen"] = board.fen()
        move_json["fen_key"] = fen_trimmer(board.fen())
        move_json["youtube_url"] = game_json["youtube_url"]
        san = board.san(move)
        board.push(move)

       
        ply += 1 

        fen.append(move_json)

    if san is not None:
        move_json = {}
        move_json["game_id"] = game_json["game_id"]
        move_json["ply"] = ply
        move_json["move_number"] = (ply + 1) // 2
        move_json["san"] = san
        move_json["side_to_move_next"] = "white" if board.turn else "black"
        move_json["fen"] = board.fen()
        move_json["fen_key"] = fen_trimmer(board.fen())
        move_json["youtube_url"] = game_json["youtube_url"]

        fen.append(move_json)

with open('data/positions.json', 'w') as f:
    json.dump(fen, f, indent=2)
        
    
