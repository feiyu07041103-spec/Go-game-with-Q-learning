This project implements a Q-learning based reinforcement learning agent to play simplified Go on a 5x5 board.
It includes:

1.AI Agent (Agent): Learns strategies using Q-learning.

2.Random Player (RandomPlayer): Provides a baseline opponent for training and evaluation.

3.Board Logic (Board): Implements Go rules such as legal moves, captures, and winner determination.

4.Game Controller (Go): Manages gameplay flow, win/loss checks, and experience replay.

5.Graphical User Interface (GoUI): Built with Tkinter, allowing interactive play against the AI.

Features:
✅ Q-learning training with reward propagation, experience pool, and replay.

✅ Rule enforcement: Legal move detection, capture mechanics, suicide prevention.

✅ Battle mode: AI vs AI or AI vs Random Player.

✅ Interactive GUI: Keyboard controls (arrow keys to move cursor, space to place stone, P to pass, Enter to restart).

✅ Model management: Save/load Q-tables, load champion models.
