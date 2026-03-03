This repository contains a simplified Go AI agent trained with Q-learning reinforcement learning on a 5x5 board.
The project demonstrates how reinforcement learning can be applied to board games, combining training scripts, core logic, and a Tkinter-based graphical interface for interactive play.

Features：

Q-learning agent with reward propagation, experience replay, and exploration decay.

Rule enforcement: legal move detection, capture mechanics, suicide prevention.

Training pipeline (train.py): automated training against random opponents, checkpoint saving, and champion model management.

Battle mode: AI vs AI or AI vs Random Player.

Interactive GUI (GOUI.py): play against the AI with keyboard controls.

Model management: save/load Q-tables, maintain best and champion models.
