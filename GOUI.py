import tkinter as tk
from GoBoard import Board, Board_size, Ongoing, Draw, X_win, O_win
from GoAgent import Agent
from GoGame import Go  # 游戏控制逻辑


class GoUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=500, height=500, bg="white")
        self.canvas.pack()
        self.cell_size = 80
        self.start = 50
        self.draw_board()

        # 初始化棋盘和AI
        self.board = Board()
        self.qlearner = Agent(side=2)  # AI 下白棋

        try:
            self.qlearner.load_QValues("Qval_CHAMPION.txt")
            print("成功加载 冠军模型Q 表")
        except Exception as e:
            print("加载 Q 表失败:", e)

        self.go_game = Go()  # 游戏控制逻辑
        self.game_over = False
        self.player_turn = True  # 重要：初始化玩家回合，True表示玩家(黑棋)的回合
        self.last_action = "MOVE"  # 记录上一次动作
        self.consecutive_passes = 0  # 连续 PASS 次数

        # 创建控制面板框架
        control_frame = tk.Frame(root)
        control_frame.pack()

        self.result_label = tk.Label(control_frame, text="", font=("Arial", 16))
        self.result_label.pack(side=tk.LEFT, padx=10)

        # 添加PASS按钮
        self.pass_button = tk.Button(control_frame, text="PASS",
                                     command=self.player_pass,
                                     bg="lightgray", font=("Arial", 12))
        self.pass_button.pack(side=tk.LEFT, padx=10)

        self.cursor_row = 2  # 初始光标放在中间
        self.cursor_col = 2  # 初始光标放在中间

        # 绑定键盘事件
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<space>", self.place_piece)
        self.root.bind("<Return>", self.restart_game)  # 回车键重新开始
        self.root.bind("<p>", self.player_pass)  # 按P键也可以PASS
        self.root.bind("<P>", self.player_pass)  # 大写P

        self.draw_cursor()

    def draw_board(self):
        end = self.start + (Board_size - 1) * self.cell_size
        for i in range(Board_size):
            self.canvas.create_line(self.start, self.start + i * self.cell_size,
                                    end, self.start + i * self.cell_size)
            self.canvas.create_line(self.start + i * self.cell_size, self.start,
                                    self.start + i * self.cell_size, end)

    def draw_piece(self, row, col, side):
        x = self.start + col * self.cell_size
        y = self.start + row * self.cell_size
        color = "black" if side == 1 else "white"
        self.canvas.create_oval(x - 30, y - 30, x + 30, y + 30, fill=color)

    def draw_cursor(self):
        self.canvas.delete("cursor")
        if not self.game_over:  # 游戏结束时隐藏光标
            x = self.start + self.cursor_col * self.cell_size
            y = self.start + self.cursor_row * self.cell_size
            self.canvas.create_rectangle(x - 35, y - 35, x + 35, y + 35,
                                         outline="red", width=2, tags="cursor")

    def refresh_board(self):
        self.canvas.delete("all")
        self.draw_board()
        for i in range(Board_size):
            for j in range(Board_size):
                if self.board.state[i][j] == 1:
                    self.draw_piece(i, j, 1)
                elif self.board.state[i][j] == 2:
                    self.draw_piece(i, j, 2)
        self.draw_cursor()

    def check_game_end(self, action):
        """检查游戏是否结束（使用GoGame的规则）"""
        # 条件1: 达到最大步数
        if self.go_game.n_moves >= self.go_game.max_moves:
            return True

        # 条件2: 连续两次 PASS
        if action == "PASS":
            self.consecutive_passes += 1
        else:
            self.consecutive_passes = 0

        if self.consecutive_passes >= 2:
            return True

        # 条件3: 棋盘没有变化且上一步是 PASS
        if action == "PASS" and self.board.compare_board(self.board.previous_board, self.board.state):
            return True

        return False

    def handle_game_over(self):
        """处理游戏结束"""
        result = self.board.check_winner()  # 这会更新 board.game_result
        self.refresh_board()

        if result == X_win:
            self.result_label.config(text="黑棋胜利！按回车键重新开始")
        elif result == O_win:
            self.result_label.config(text="白棋胜利！按回车键重新开始")
        elif result == Draw:
            self.result_label.config(text="平局！按回车键重新开始")

        self.game_over = True
        self.player_turn = False  # 游戏结束，玩家回合设为False
        self.canvas.delete("cursor")  # 删除光标
        print(f"游戏结束！结果: {self.result_label.cget('text')}")

    def check_game_over_unified(self):
        """统一的游戏结束检查（直接调用check_game_end）"""
        if self.check_game_end(self.last_action):
            self.handle_game_over()
            return True
        return False

    def player_pass(self, event=None):
        """玩家选择PASS"""
        if self.game_over:
            print("游戏已结束，不能PASS")
            return

        if not self.player_turn:
            print("现在不是你的回合")
            return

        print("玩家选择 PASS")

        # 记录上一步棋盘状态
        self.board.previous_board = self.board.state.copy()

        # 更新状态
        self.go_game.n_moves += 1
        self.last_action = "PASS"
        self.player_turn = False

        # 检查游戏是否结束
        if self.check_game_over_unified():
            return

        # AI 回合
        print("AI 思考中...")
        self.root.update()

        # AI 移动
        self.ai_move()

    def place_piece(self, event):
        if self.game_over:
            print("游戏已结束，按键无效")
            return

        if not self.player_turn:
            print("现在不是你的回合")
            return

        # 玩家落子
        row, col = self.cursor_row, self.cursor_col
        if self.board.is_valid_move(row, col, 1):
            # 记录上一步棋盘状态
            self.board.previous_board = self.board.state.copy()

            # 玩家落子
            self.board.move(row, col, 1)
            # 移除被提掉的白棋
            died_pieces = self.board.remove_died_pieces(2)
            if died_pieces:
                print(f"提掉白棋: {died_pieces}")

            self.refresh_board()
            self.go_game.n_moves += 1
            self.last_action = "MOVE"
            self.player_turn = False

            # 检查游戏是否结束
            if self.check_game_over_unified():
                return

            # AI 回合
            print("AI 思考中...")
            self.root.update()  # 更新界面

            # AI 移动
            self.ai_move()
        else:
            print("非法落子")

    def ai_move(self):
        """AI落子"""
        # 记录AI移动前的棋盘状态
        self.board.previous_board = self.board.state.copy()

        # AI 移动
        action = self.qlearner.move(self.board)

        if action != "PASS":
            row, col = action
            print(f"AI 落子: ({row}, {col})")
            # 移除被提掉的黑棋
            died_pieces = self.board.remove_died_pieces(1)
            if died_pieces:
                print(f"AI提掉黑棋: {died_pieces}")
            self.go_game.n_moves += 1
            self.last_action = "MOVE"
        else:
            print("AI 选择 PASS")
            self.last_action = "PASS"
            self.go_game.n_moves += 1

        self.refresh_board()
        self.player_turn = True

        # 再次检查游戏是否结束
        self.check_game_over_unified()

    def restart_game(self, event):
        """重新开始游戏"""
        self.board.reset()
        self.go_game.n_moves = 0
        self.go_game.X_move = True
        self.last_action = "MOVE"
        self.consecutive_passes = 0
        self.player_turn = True  # 玩家先手
        self.refresh_board()
        self.result_label.config(text="")
        self.game_over = False
        self.cursor_row, self.cursor_col = 2, 2  # 重置光标到中间
        self.draw_cursor()
        print("新的一局开始！")

    def move_up(self, event):
        if not self.game_over and self.player_turn:  # 只有玩家回合才能移动光标
            if self.cursor_row > 0:
                self.cursor_row -= 1
                self.draw_cursor()

    def move_down(self, event):
        if not self.game_over and self.player_turn:
            if self.cursor_row < Board_size - 1:
                self.cursor_row += 1
                self.draw_cursor()

    def move_left(self, event):
        if not self.game_over and self.player_turn:
            if self.cursor_col > 0:
                self.cursor_col -= 1
                self.draw_cursor()

    def move_right(self, event):
        if not self.game_over and self.player_turn:
            if self.cursor_col < Board_size - 1:
                self.cursor_col += 1
                self.draw_cursor()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Go Game")
    ui = GoUI(root)
    root.mainloop()