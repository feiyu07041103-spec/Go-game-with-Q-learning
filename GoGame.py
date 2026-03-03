from copy import deepcopy
import numpy as np
from GoBoard import Board, Ongoing, Draw, X_win, O_win


class Go:
    def __init__(self):
        self.n_moves = 0
        self.max_moves = 35  # 5x5棋盘最多35步
        self.X_move = True  # True表示黑棋先手
        self.pass_count = 0  # 连续pass次数

    def game_end(self, board, action="MOVE"):
        """检查游戏是否结束"""
        # 达到最大步数
        if self.n_moves >= self.max_moves:
            return True

        # 连续两次PASS
        if action == "PASS":
            self.pass_count += 1
            if self.pass_count >= 2:
                return True
        else:
            self.pass_count = 0

        # 棋盘无变化且上一步是PASS
        if action == "PASS" and board.compare_board(board.previous_board, board.state):
            self.pass_count += 1
            if self.pass_count >= 2:
                return True

        return False

    def play(self, board, player1, player2, learn=True):
        """进行一局对弈"""
        action = "MOVE"
        self.n_moves = 0
        self.pass_count = 0
        self.X_move = True

        while True:
            piece_type = 1 if self.X_move else 2
            current_player = player1 if piece_type == 1 else player2

            # 检查游戏是否结束
            if self.game_end(board, action):
                result = board.check_winner()
                if learn:
                    # 只有AI才需要学习
                    if hasattr(player1, 'learn_from_game'):
                        player1.learn_from_game(board)
                    if hasattr(player2, 'learn_from_game'):
                        player2.learn_from_game(board)
                return result

            # 执行移动
            action = current_player.move(board)
            self.n_moves += 1
            self.X_move = not self.X_move

    def battle(self, player1, player2, games, learn=True, show_result=True):
        """多局对战"""
        player1.set_side(1)
        player2.set_side(2)

        stats = [0, 0, 0]  # [平局, 黑胜, 白胜]

        for i in range(games):
            if i % 100 == 0 and i > 0:
                print(f"  已完成 {i} 局")

            board = Board()
            result = self.play(board, player1, player2, learn)
            stats[result] += 1

            # 定期经验回放（只有AI才需要）
            if learn and i % 10 == 0:
                if hasattr(player1, 'replay_experience'):
                    player1.replay_experience()
                if hasattr(player2, 'replay_experience'):
                    player2.replay_experience()

        # 计算百分比
        p1_stats = [round(x / games * 100, 1) for x in stats]

        if show_result:
            print("\n" + "=" * 60)
            print(f" 对战结果 ({games}局)")
            print(f"黑棋 ({player1.name}) | 胜:{p1_stats[1]}% 平:{p1_stats[0]}% 负:{p1_stats[2]}%")
            print(f"白棋 ({player2.name}) | 胜:{p1_stats[2]}% 平:{p1_stats[0]}% 负:{p1_stats[1]}%")
            print("=" * 60)

        return p1_stats