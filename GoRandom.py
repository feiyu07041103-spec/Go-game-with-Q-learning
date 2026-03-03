import numpy as np


class RandomPlayer:
    def __init__(self, side=None, name="Random"):
        self.side = side
        self.name = name

    def set_side(self, side):
        self.side = side

    def move(self, board):
        legal_moves = board.get_legal_moves(self.side)

        if not legal_moves:
            return "PASS"

        idx = np.random.randint(len(legal_moves))
        row, col = legal_moves[idx]
        board.move(row, col, self.side)
        board.remove_died_pieces(3 - self.side)
        return row, col

    def learn_from_game(self, board):
        """随机玩家不学习，这个方法什么都不做"""
        pass

    def replay_experience(self):
        """随机玩家不学习"""
        return 0

    def get_stats(self):
        return {"states": 0, "epsilon": 0, "experience_pool": 0}