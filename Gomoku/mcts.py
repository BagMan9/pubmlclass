# This allows for self-referential typing (MCTSNode)
from __future__ import annotations

import math
import random
from decimal import InvalidContext
from typing import Literal

import numpy as np

WIN_LINES = [
    [(0, 0), (0, 1), (0, 2)],  # rows
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],  # cols
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],  # diagonals
    [(0, 2), (1, 1), (2, 0)],
]

RENDER = [" ", "X", "O"]


class GameBoard:
    def __init__(self, size: int, entries: None | np.ndarray = None):
        self.size = size
        self.entries = (
            np.zeros(dtype=np.uint8, shape=(size, size + (16 if size <= 16 else 32)))
            if entries is None
            else np.array(entries, copy=True)
        )

    def __str__(self):
        ret = ""
        for i in range(self.size):
            space = "|".join([RENDER[self.entries[i][x]] for x in range(self.size)])
            ret = ret + space + "\n"
            if i < self.size - 1:
                ret = ret + "-----\n"
        return ret[:-1]

    def checkwin(self) -> Literal[0, 1, 2, 3]:
        for line in WIN_LINES:
            vals = [self.entries[r][c] for r, c in line]
            if vals == [1, 1, 1]:
                return 1
            if vals == [2, 2, 2]:
                return 2
        if any(0 in row for row in self.entries):
            return 0
        return 3

    def check_nextplayer(self, bd: np.ndarray | None = None):
        if bd is None:
            bd = self.entries
        count_1 = sum(cc == 1 for row in bd for cc in row)
        count_2 = sum(cc == 2 for row in bd for cc in row)
        return 1 if count_1 == count_2 else 2

    def getmoves(self):
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.entries[r][c] == 0
        ]  # all possible position where the board is empty

    def copy(self):
        new_board = GameBoard(self.size, self.entries)
        return new_board


class MCTSNode:
    def __init__(
        self, bd: GameBoard, parent: MCTSNode | None, action: tuple[int, int] | None
    ):
        self.bd = bd
        self.parent = parent
        self.action = action  # action that led to this node
        self.children = []  # list of child nodes
        self.possible_moves = bd.getmoves()  # moves that can be played from this node
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self):
        return len(self.possible_moves) == 0

    def is_terminal(self):
        return self.bd.checkwin() != 0


def apply_action(bd: GameBoard, action, player):
    r, c = action
    new_bd = bd.copy()
    new_bd.entries[r][c] = player
    return new_bd


DEFAULT_C = math.sqrt(2)


class MCTS:
    def __init__(self, c: float | int = DEFAULT_C):
        self.c = c

    def uct_select(self, node: MCTSNode, c=None) -> MCTSNode:
        # node: current node
        # return: child node with highest UCT value
        if c is None:
            c = self.c
        return max(
            node.children,
            key=lambda child: (child.wins / child.visits)
            + c * math.sqrt(math.log(node.visits) / child.visits),
        )

    def expand(self, node: MCTSNode) -> MCTSNode:
        # node: current node
        # return: new child node after applying one of the possible moves

        action = node.possible_moves.pop()
        r, c = action

        child_bd = node.bd.copy()
        player = child_bd.check_nextplayer(child_bd.entries)
        child_bd = apply_action(child_bd, action, player)

        child_node = MCTSNode(child_bd, parent=node, action=action)
        node.children.append(child_node)
        return child_node

    def rollout(self, bd: GameBoard) -> int:
        # bd: current board
        # return: score on the same (+1: for winner player)

        rollout_bd = bd.copy()

        while rollout_bd.checkwin() == 0:
            next_player = rollout_bd.check_nextplayer(rollout_bd.entries)
            actions = rollout_bd.getmoves()
            if not actions:
                break
            action = random.choice(actions)
            rollout_bd = apply_action(rollout_bd, action, next_player)

        winner = rollout_bd.checkwin()
        if winner == 1 or winner == 2:
            return +1
        else:
            return 0

    def backpropagate(self, node: MCTSNode, reward: int):
        current = node
        while current is not None:
            current.visits += 1
            current.wins += reward
            # switch perspective
            reward = -reward

            # propagate to parent
            current = current.parent

    def search(self, root: MCTSNode, iter=2000) -> tuple[int, int]:
        # based on the rood board, run MCTS and return the best action
        # root = MCTSNode(root_bd, parent=None, action=None)
        root_bd = root.bd
        if root_bd.checkwin() != 0:
            raise ValueError("Game is over")

        for _ in range(iter):
            node = root

            # selection
            while (not node.is_terminal()) and node.is_fully_expanded():
                node = self.uct_select(node, c=self.c)

            # expansion
            if (not node.is_terminal()) and (not node.is_fully_expanded()):
                node = self.expand(node)

            # simulation
            reward = self.rollout(node.bd)

            # backpropagation
            self.backpropagate(node, reward)
        self.c = 0
        best_child = self.uct_select(root, c=0)
        if best_child.action is None:
            raise InvalidContext("This probably shouldn't happen?")
        return best_child.action


def MCTS_move(root_state: GameBoard, iterations=2000):
    mcts = MCTS()
    root_node = MCTSNode(bd=root_state, parent=None, action=None)

    best_action = mcts.search(root_node, iter=iterations)
    player = root_state.check_nextplayer(root_state.entries)
    next_state = apply_action(root_state, best_action, player)

    return best_action, player, next_state


def prompt_human(bd: GameBoard) -> tuple[int, int]:
    print("Please choose a space!")
    validinput = False
    humanrow, humancol = -1, -1

    while not validinput:
        user_input = input("Enter two numbers separated by a comma: ")

        if len(user_input) != 3 or user_input[1] != ",":
            print("The format is num,num")
            continue
        if not user_input[0].isdigit() or not user_input[2].isdigit():
            print("Please enter numbers!")
            continue
        # FIXME: Hard coded game board length

        humanrow, humancol = map(int, map(str.strip, user_input.split(",")))
        if not humanrow < bd.size or not humancol < bd.size:
            print("Entry does not exist on board")
            continue
        if bd.entries[humanrow][humancol] != 0:
            print("Spot already taken, try another!")
            continue
        validinput = True
    if humanrow == -1 or humancol == -1:
        raise InterruptedError("Something has gone horribly wrong")
    return humanrow, humancol


if __name__ == "__main__":
    bd = GameBoard(4)
    valid_player = False
    choice = ""
    iters = input(
        "Please enter how many iterations MCTS should use per search (Default: 2000): "
    )
    if not iters.isdigit():
        iters = 2000
        print(f"Using default value of {iters} iterations")
    else:
        iters = int(iters)
    human: Literal[1, 2] = 1
    bot: Literal[1, 2] = 2
    while not valid_player:
        choice = input("Player X or O: ")
        if len(choice) != 1:
            continue
        choice = choice.upper()
        if choice != "X" and choice != "O":
            continue
        valid_player = True
    if choice == "O":
        human = 2
        bot = 1
    print(bd)
    while bd.checkwin() == 0:
        curplayer = bd.check_nextplayer()
        if curplayer == human:
            row, col = prompt_human(bd)
            bd.entries[row][col] = human
            print("Your move:")
            print(bd)
        else:
            (row, col), _, _ = MCTS_move(bd, iters)
            bd.entries[row][col] = bot
            print("AI Move:")
            print(bd)
    LOOKUP = ["X wins!", "O wins!", "Draw!"]
    print(LOOKUP[bd.checkwin() - 1])
