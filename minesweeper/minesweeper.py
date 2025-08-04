import itertools
import random


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

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
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

        # If we have a set of cells and the size of the set is equal to the count. We know all cells are mines
        if len(self.cells) == self.count:
            return self.cells
        
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # If we have a set filled with cells, and said count is 0. We know all cells are safe
        if self.cells and self.count == 0:
            return self.cells
        
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

        return 

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells: 
            self.cells.remove(cell)

        return

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
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
        
        # First mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Second mark cell as safe
        self.mark_safe(cell)

        # Third add a sentende based on the value of cell and count
        # Gets all the neighbors of cell
        neighbors = self.get_neighbors(cell)
        unknown_neighbors = set()
        adjusted_count = count

        # Goes through neighbors, if it is a mine lower the count
        # If it is not in safe that means we dont know what it is so we add it to unknown
        for neighbor in neighbors:
            if neighbor in self.mines:
                adjusted_count -= 1
            elif neighbor not in self.safes:
                unknown_neighbors.add(neighbor)

        # Now with our unknown neighbors, we append the new count with the neighbors
        if unknown_neighbors:
            self.knowledge.append(Sentence(unknown_neighbors, adjusted_count))

        # Fourth mark any additional cells as safe or as mines
        changed = True
        while changed:
            changed = False
            safes = set()
            mines = set()

            # Iterate through the knowledge base
            for sentence in self.knowledge:
                # If we know the safes, add it to the set
                if sentence.known_safes():
                    safes |= sentence.known_safes()

                # If we know the mines, add it to the set
                if sentence.known_mines():
                    mines |= sentence.known_mines()

            for safe in safes:
                # If we have discovered a new safe
                if safe not in self.safes:
                    self.mark_safe(safe)
                    # Mark changed as true
                    changed = True

            for mine in mines:
                # If we discover a new mine
                if mine not in self.mines:
                    self.mark_mine(mine)
                    changed = True

            

        # Fifth add sentences to the knowledge base if they can be inferred
        new_info = []
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                # If theyre equal to each other, or cells are empty
                if s1 == s2 or not s1.cells or not s2.cells:
                    continue

                if s2.cells.issubset(s1.cells):
                    # If the cells are a subset of each other
                    new_cells = s1.cells - s2.cells
                    new_count = s1.count - s2.count
                    # Create the new sentence
                    new_sentence = Sentence(new_cells, new_count)

                    # If the new sentence is not already present in knowledge and new info
                    # If new cells actually contains cells
                    # Add it to the new info
                    if (new_sentence not in self.knowledge) and (new_sentence not in new_info) and (new_cells):
                        new_info.append(new_sentence)

        self.knowledge.extend(new_info)

        
        
        
        return
                    

            


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
            
        
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                random_cell = i, j

                if random_cell not in self.moves_made and random_cell not in self.mines:
                    possible_moves.append(random_cell)

        if possible_moves:
            return random.choice(possible_moves)

        else:
            return None        
        
    def get_neighbors(self, cell):
        neighbors = set()

        directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]

        for direction in directions:
            new_cell = (direction[0] + cell[0], direction[1] + cell[1])
            if 0 <= new_cell[0] < self.height and 0 <= new_cell[1] < self.width:
                neighbors.add(new_cell)

        return neighbors

