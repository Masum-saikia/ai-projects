import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """
        count = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        for i in self.knowledge:
            print(i)
        cell_list = []
        c = count
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:        
                    if (i, j) in self.mines:
                        c -= 1
                    elif (i, j) in self.safes:
                        pass
                    else:
                        cell_list.append((i, j))
        self.knowledge.append(Sentence(cell_list, c))
        if c == 0:
            for i in cell_list:
                self.mark_safe(i)
        
        def safe_adder():
            changed = False
            for _ in range(len(self.knowledge)):
                changed = False
                for sentence in self.knowledge:
                    if len(sentence.cells) > 0 and sentence.count == 0:
                        for i in copy.deepcopy(sentence.cells):
                            self.mark_safe(i)
                            changed = True
                    if len(sentence.cells) > 0 and len(sentence.cells) == sentence.count:
                        for i in copy.deepcopy(sentence.cells):
                            self.mark_mine(i)
                            changed = True
                if not changed:
                    break
        safe_adder()
        for i in copy.deepcopy(self.knowledge):
            if len(i.cells) == 0:
                continue
            for j in copy.deepcopy(self.knowledge):
                if len(j.cells) == 0 or i.cells == j.cells:
                    continue
                if i.cells.issubset(j.cells):
                    self.knowledge.append(Sentence(i.cells.symmetric_difference(j.cells), abs(i.count-j.count)))

        safe_adder()
        for i in copy.deepcopy(self.knowledge):
            occ = len([1 for j in self.knowledge if j.cells==i.cells])-1  
            while occ>1:
                try:
                    self.knowledge.remove(i)
                    occ-=1
                except:
                    occ = 0     
        for i in self.knowledge:
            print(i)
        for i in copy.deepcopy(self.knowledge):
            if i.cells == set():
                self.knowledge.remove(i)                
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        possible_moves = self.safes-self.moves_made
        if len(possible_moves) != 0:
            return possible_moves.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        while True:
            if len(self.moves_made) == (self.height*self.width)-len(self.mines):
                print("Only mines are left on board")
                return
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines:
                return (i, j)