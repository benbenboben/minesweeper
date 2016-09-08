"""
Minesweeper source code
"""

import copy
import numpy as np


class MinesweeperBoard(object):
    """
    class to solve minesweeper move for a given board
    board must be 9x9 (for now)
    board must have:
        blanks " " for non contributing cells
        '?' for unknowns
        numerical values for clues
    """

    def __init__(self):
        """
        initialize MinesweeperBoard object
        stores the board, bomb locations, and safe moves
        should change this to only store the board and the graph
        """
        self.board_ = MinesweeperBoard.read_board_()
        self.bomb_locations_ = set()
        self.safe_moves_ = set()
        self.graph_ = dict()

    @staticmethod
    def read_board_():
        """
        reads board from board.txt file as a 2d numpy array
        assumes 9x9, this could be generalized
        """
        board = np.ndarray((9, 9), dtype='object')
        with open('board.txt', 'r') as fobj:
            lines = fobj.readlines()
        for iline, line in enumerate(lines):
            parsed = np.asarray([c for c in line if c != '\n'], dtype='object')
            board[iline, :] = parsed
        return board

    def __str__(self):
        """
        converts board to readable format
        makes no assumptions on board dimensions
        """
        out = ""
        for i in range(self.board_.shape[0]):
            line = [x for x in self.board_[i, :]]
            out += " ".join(line) + '\n'
        return out

    def get_clue_indices_(self):
        """
        finds the indicies with numbers in them
        """
        i_x = np.in1d(self.board_.ravel(), [str(x) for x in range(1, 11)])
        i_x = i_x.reshape(self.board_.shape)
        indices = list(zip(np.where(i_x)[0], np.where(i_x)[1]))
        return indices

    def make_graph_(self):
        """
        makes a graph of all clues (numerical cells) connected to all suspects (? cells)
        graph will store:
            number of bombs (numerical value)
            suspects (indices of connected ?)
            and safe moves (? that are guaranteed safe)
        """
        #self.graph_ = dict()
        for idx in self.get_clue_indices_():
            self.graph_[idx] = {'bombs': int(self.board_[idx]),
                                'suspects': self.find_adjacent_suspects_(idx),
                                'safe_moves': set()}
        #return graph

    def graph_deduction_(self):
        """
        builds graph and deduces where bombs are
        lazily checks to see if graph has changed from previous iteration
        """
        self.make_graph_()
        tmp_graph = copy.deepcopy(self.graph_)
        while True:
            self.guaranteed_bombs_()
            #for bomb in bombs:
            #    self.bomb_locations_.add(bomb)
            self.reduce_graph_for_bomb_()
            self.mark_bomb_()
            if self.graph_ == tmp_graph:
                break
            else:
                tmp_graph = copy.deepcopy(self.graph_)
            #print(str(self))
        #return graph

    def reduce_graph_for_bomb_(self):
        """
        for found bombs (indices in bombs), the graph is tailored:
            removes bombs from suspects
            decrement number of bombs for a node
            if number of bombs is reduced to zero, all suspects (that are not bomb) are safe moves
        """
        to_remove = []
        for clue in self.graph_.keys():
            for suspect in self.graph_[clue]['suspects']:
                if suspect in self.bomb_locations_:
                    self.graph_[clue]['bombs'] -= 1
            if self.graph_[clue]['bombs'] == 0:
                to_remove += [i for i in self.graph_[clue]['suspects'] if i not in to_remove]
                self.graph_[clue]['safe_moves'] |= set([i for i in self.graph_[clue]['suspects'] if i not in self.bomb_locations_])
                #for i in self.graph_[clue]['safe_moves']:
                #    self.safe_moves_.add(i)
                self.graph_[clue]['suspects'] = []
        to_remove += [b for b in self.bomb_locations_ if b not in to_remove]
        for clue in self.graph_.keys():
            self.graph_[clue]['suspects'] = [i for i in self.graph_[clue]['suspects'] if i not in to_remove]
        #return graph

    def mark_bomb_(self):
        """
        updates board with guaranteed bomb locations
        """
        for bomb in self.bomb_locations_:
            self.board_[bomb] = "*"

    def guaranteed_bombs_(self):
        """"
        analyzes graph to see where guaranteed bombs are
        if number of suspects is equal to number of bombs, a guaranteed bomb has been found
        these are added to the bombs list (will be reduced from graph in separate routine)
        """
        #bombs = []
        for key in self.graph_.keys():
            if len(self.graph_[key]['suspects']) == self.graph_[key]['bombs']:
                #for i in self.graph_[key]['suspects']:
                self.bomb_locations_.update(tuple(self.graph_[key]['suspects']))
        #return bombs

    def find_adjacent_suspects_(self, idx):
        """
        for a given index of the board, all suspect (?) indices touching said index
        will be return (index should be a clue, this is not enforced here)
        """
        min_x = max(idx[0] - 1, 0)
        max_x = min(idx[0] + 1, 9)
        min_y = max(idx[1] - 1, 0)
        max_y = min(idx[1] + 1, 9)
        suspects = []
        for i_x in range(min_x, max_x + 1):
            for i_y in range(min_y, max_y + 1):
                if self.board_[i_x, i_y] == '?':
                    suspects.append((i_x, i_y))
        return suspects

    def make_safe_moves_(self):
        for key in self.graph_.keys():
            self.safe_moves_.update(tuple([i for i in self.graph_[key]['safe_moves']]))


def main():
    """
    runs minesweeper
    """
    board = MinesweeperBoard()
    print("Board to solve")
    print(str(board))
    board.make_graph_()
    graph = board.graph_deduction_()
    print("Board with mines")
    print(str(board))
    #print(board.bomb_locations_)
    #board.safe_moves_ = [i for i in board.safe_moves_ if i not in board.bomb_locations_]
    board.make_safe_moves_()
    #print(board.safe_moves_)
    print("Guaranteed safe moves")
    print(sorted(board.safe_moves_))

if __name__ == '__main__':
    main()
