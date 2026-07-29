import json 
import chess.pgn
import io

with open('games.json') as f:
    games = json.load(f)

fen = []

for game_json in games: 
    game = chess.pgn.read_game(io.StringIO(game_json["pgn_moves"]))
    board = game.board()
    
    ply = 1 

    for move in game.mainline_moves():
        move_json = {}
        san = board.san(move)
        board.push(move)
        move_json["game_id"] = game_json["game_id"]
        move_json["ply"] = ply
        move_json["move_number"] = (ply + 1) // 2
        move_json["san"] = san
        move_json["side_to_move_next"] = "white" if board.turn else "black"
        move_json["fen"] = board.fen()
        move_json["fen_key"] = " ".join(board.fen().split(" ")[:-2])
        move_json["youtube_url"] = game_json["youtube_url"]

       
        ply += 1 

        fen.append(move_json)

print(fen[0:30])
        
    
