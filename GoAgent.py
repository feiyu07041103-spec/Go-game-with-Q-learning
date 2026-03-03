from copy import deepcopy
import numpy as np
import json
import os
from GoBoard import Draw, X_win, O_win

# 超参数
WIN_REWARD = 1.0
DRAW_REWARD = 0.3
LOSS_REWARD = 0.0
CAPTURE_REWARD = 0.2  # 每提一子的奖励
LEARNING_RATE = 0.1
DISCOUNT = 0.9
EXPLORATION_RATE = 0.2  # 探索率
EXPLORATION_DECAY = 0.999  # 探索率衰减
MIN_EXPLORATION = 0.05


class Agent:
    def __init__(self, side=None, name="AI"):
        self.side = side
        self.name = name
        self.alpha = LEARNING_RATE
        self.gamma = DISCOUNT
        self.epsilon = EXPLORATION_RATE
        self.q_values = {}  # Q表: state -> 5x5矩阵
        self.history = []  # 当前对局历史
        self.experience_pool = []  # 经验池
        self.pool_size = 10000
        self.batch_size = 32
        self.initial_value = 0.5

        # 开局偏好（天元和中腹价值稍高）
        self.initial_q = np.array([
            [0.3, 0.4, 0.4, 0.4, 0.3],
            [0.4, 0.6, 0.7, 0.6, 0.4],
            [0.4, 0.7, 0.8, 0.7, 0.4],
            [0.4, 0.6, 0.7, 0.6, 0.4],
            [0.3, 0.4, 0.4, 0.4, 0.3]
        ])

    def set_side(self, side):
        self.side = side

    def Q(self, state):
        """获取状态的Q值矩阵，如果不存在则初始化"""
        if state not in self.q_values:
            self.q_values[state] = self.initial_q.copy()
        return self.q_values[state]

    def _select_best_move(self, board):
        """选择最佳落子位置（ε-greedy）"""
        state = board.encode_state()
        q_values = self.Q(state)
        legal_moves = board.get_legal_moves(self.side)

        if not legal_moves:
            return "PASS"

        # ε-greedy: 以epsilon的概率随机探索
        if np.random.random() < self.epsilon:
            idx = np.random.randint(len(legal_moves))
            return legal_moves[idx]

        # 否则选择Q值最大的合法位置
        best_move = None
        best_value = -float('inf')

        # 将非法位置设为负无穷
        for i in range(5):
            for j in range(5):
                if (i, j) not in legal_moves:
                    q_values[i][j] = -float('inf')

        # 找到最大值
        max_q = np.max(q_values)
        candidates = []
        for i, j in legal_moves:
            if q_values[i][j] >= max_q - 1e-6:  # 允许浮点误差
                candidates.append((i, j))

        # 从最大Q值中随机选一个（打破平局）
        if candidates:
            return candidates[np.random.randint(len(candidates))]
        return "PASS"

    def move(self, board):
        """执行一步移动"""
        result = self._select_best_move(board)

        if result == "PASS":
            self.history.append((board.encode_state(), "PASS", 0))
            return "PASS"

        row, col = result
        state_before = board.encode_state()

        # 计算提子前对方棋子数量
        opponent = 3 - self.side
        opponent_before = board.score(opponent)

        # 执行落子
        board.move(row, col, self.side)

        # 提子
        captured = board.remove_died_pieces(opponent)
        capture_count = len(captured)

        # 检查是否提掉对方棋子
        opponent_after = board.score(opponent)
        captured_count = opponent_before - opponent_after

        # 即时奖励：提子奖励
        immediate_reward = captured_count * CAPTURE_REWARD

        # 记录历史 (统一使用3个值: state, move, immediate_reward)
        self.history.append((state_before, (row, col), immediate_reward))

        return row, col

    def learn_from_game(self, board):
        """一局结束后学习"""
        # 终局奖励
        if board.game_result == Draw:
            final_reward = DRAW_REWARD
        elif board.game_result == self.side:
            final_reward = WIN_REWARD
        else:
            final_reward = LOSS_REWARD

        # 反向传播更新Q值
        self.history.reverse()
        max_q_value = -float('inf')

        for item in self.history:
            # 统一处理不同长度的历史记录
            if len(item) == 3:
                state, move, immediate_reward = item
            elif len(item) == 2:  # 兼容旧版本
                state, move = item
                immediate_reward = 0
            else:
                continue

            if move == "PASS":
                continue

            q = self.Q(state)
            row, col = move

            if max_q_value == -float('inf'):  # 最后一步
                # 最后一步的奖励 = 即时奖励 + 终局奖励
                total_reward = immediate_reward + final_reward
                q[row][col] = total_reward
                max_q_value = total_reward
            else:
                # 中间步的奖励 = 即时奖励 + 折扣后的未来最大价值
                current_q = q[row][col]
                target = immediate_reward + self.gamma * max_q_value
                q[row][col] = current_q + self.alpha * (target - current_q)
                max_q_value = np.max(q)

            # 保存到经验池
            self.experience_pool.append((state, move, immediate_reward, final_reward))

        # 限制经验池大小
        if len(self.experience_pool) > self.pool_size:
            self.experience_pool = self.experience_pool[-self.pool_size:]

        # 清空历史
        self.history = []

        # 探索率衰减
        self.epsilon = max(MIN_EXPLORATION, self.epsilon * EXPLORATION_DECAY)

    def replay_experience(self):
        """经验回放：从经验池中随机学习"""
        if len(self.experience_pool) < self.batch_size:
            return 0

        # 随机抽取一批经验
        batch = np.random.choice(len(self.experience_pool), self.batch_size, replace=False)

        updates = 0
        for idx in batch:
            state, move, immediate_reward, final_reward = self.experience_pool[idx]

            if move == "PASS":
                continue

            q = self.Q(state)
            row, col = move

            # 简化的更新
            current_q = q[row][col]
            target = immediate_reward + 0.5 * final_reward
            q[row][col] = current_q + 0.05 * (target - current_q)
            updates += 1

        return updates

    def save_QValues(self, filename="Qval.txt"):
        """保存Q表"""
        # 转换为可序列化格式
        serializable = {}
        for state, values in self.q_values.items():
            serializable[state] = json.dumps(values.tolist())

        with open(filename, 'w') as f:
            json.dump(serializable, f)

        print(f" Q表已保存到 {filename}，包含 {len(self.q_values)} 个状态")

    def load_QValues(self, filename="Qval.txt"):
        """加载Q表"""
        if not os.path.exists(filename):
            print(f" 文件 {filename} 不存在，使用初始Q表")
            return

        with open(filename, 'r') as f:
            serializable = json.load(f)

        self.q_values = {}
        for state, values_str in serializable.items():
            self.q_values[state] = np.array(json.loads(values_str))

        print(f" 成功加载 {len(self.q_values)} 个状态的Q值")

    def get_stats(self):
        """获取统计信息"""
        return {
            "states": len(self.q_values),
            "epsilon": self.epsilon,
            "experience_pool": len(self.experience_pool)
        }