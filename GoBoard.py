from copy import deepcopy
import numpy as np

Board_size = 5
Ongoing = -1
Draw = 0
X_win = 1
O_win = 2


class Board:
    def __init__(self, state=None):
        if state is None:
            self.state = np.zeros((Board_size, Board_size), dtype=int)
        else:
            self.state = state.copy()

        self.game_result = Ongoing
        self.previous_board = deepcopy(self.state)
        self.died_pieces = []
        self.last_move = None
        self.move_count = 0

    def encode_state(self):
        """将棋盘编码为字符串，作为Q表的键"""
        return ''.join(str(self.state[i][j]) for i in range(Board_size)
                       for j in range(Board_size))

    def reset(self):
        self.state.fill(0)
        self.game_result = Ongoing
        self.previous_board = deepcopy(self.state)
        self.died_pieces = []
        self.last_move = None
        self.move_count = 0

    def copy_board(self):
        return deepcopy(self)

    def is_valid_move(self, row, col, piece_type):
        """检查落子是否合法"""
        if row < 0 or row >= Board_size or col < 0 or col >= Board_size:
            return False
        if self.state[row][col] != 0:
            return False

        # 模拟落子检查是否自杀
        temp_board = self.copy_board()
        temp_board.state[row][col] = piece_type
        if not temp_board.find_liberty(row, col):
            # 如果落子后没气，但能提掉对方棋子，也是合法
            opponent = 3 - piece_type
            died = temp_board.find_died_pieces(opponent)
            if not died:
                return False
        return True

    def detect_neighbor(self, i, j):
        """返回相邻位置"""
        neighbors = []
        if i > 0: neighbors.append((i - 1, j))
        if i < Board_size - 1: neighbors.append((i + 1, j))
        if j > 0: neighbors.append((i, j - 1))
        if j < Board_size - 1: neighbors.append((i, j + 1))
        return neighbors

    def detect_neighbor_ally(self, row, col):
        """返回同色的相邻棋子"""
        allies = []
        neighbors = self.detect_neighbor(row, col)
        for piece in neighbors:
            if self.state[piece[0]][piece[1]] == self.state[row][col]:
                allies.append(piece)
        return allies

    def ally_dfs(self, row, col):
        """DFS找到所有相连的同色棋子"""
        stack = [(row, col)]
        ally_members = []
        while stack:
            piece = stack.pop()
            if piece not in ally_members:
                ally_members.append(piece)
                neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
                for ally in neighbor_allies:
                    if ally not in ally_members and ally not in stack:
                        stack.append(ally)
        return ally_members

    def find_liberty(self, row, col):
        """检查棋子是否有气"""
        ally_members = self.ally_dfs(row, col)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                if self.state[piece[0]][piece[1]] == 0:
                    return True
        return False

    def find_died_pieces(self, piece_type):
        """找到所有死子"""
        died = []
        for i in range(Board_size):
            for j in range(Board_size):
                if self.state[i][j] == piece_type:
                    if not self.find_liberty(i, j):
                        died.append((i, j))
        return died

    def remove_died_pieces(self, piece_type):
        """移除死子并返回被提的子"""
        died = self.find_died_pieces(piece_type)
        if died:
            for r, c in died:
                self.state[r][c] = 0
        return died

    def move(self, row, col, player):
        """落子"""
        self.previous_board = deepcopy(self.state)
        self.state[row][col] = player
        self.last_move = (row, col)
        self.move_count += 1
        return True

    def compare_board(self, board1, board2):
        """比较两个棋盘是否相同"""
        return np.array_equal(board1, board2)

    def score(self, piece_type):
        """计算某色棋子数量"""
        return np.sum(self.state == piece_type)

    def check_winner(self):
        """判断胜负"""
        cnt1 = self.score(1)
        cnt2 = self.score(2)
        if cnt1 > cnt2:
            winner = X_win
        elif cnt2 > cnt1:
            winner = O_win
        else:
            winner = Draw
        self.game_result = winner
        return winner

    def get_empty_positions(self):
        """获取所有空位"""
        empty = []
        for i in range(Board_size):
            for j in range(Board_size):
                if self.state[i][j] == 0:
                    empty.append((i, j))
        return empty

    def get_legal_moves(self, piece_type):
        """获取所有合法落子位置"""
        legal = []
        for i in range(Board_size):
            for j in range(Board_size):
                if self.is_valid_move(i, j, piece_type):
                    legal.append((i, j))
        return legal