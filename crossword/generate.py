import sys
from PIL import Image, ImageDraw, ImageFont
from crossword import Variable, Crossword
from collections import deque


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        # First we need to enforce the unary constraints
        # We must go through every variable and remove the domain value that is not the length of the variable

        # We iterate through each variable in the dict
        for var in self.domains:
            # We then go through each word in the key set
            for word in self.domains[var].copy():
                # If the length of the word does not match the length of the variable
                if var.length != len(word):
                    # We remove it
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # We create a revised variable to know if we have revised it
        revised = False
        # Assign a variable to the overlap pair
        overlap = self.crossword.overlaps[x, y]

        # We check if x and y even overlap
        if overlap is not None:
            # Assign a variable each index of the overlap pair
            x_o = overlap[0]
            y_o = overlap[1]
            # If they overlap iterate through x domain
            for X in self.domains[x].copy():
                # Create a found variable to indiciate if we found an arc between two vars
                found = False
                # Iterate through y domain to see if we can find a match
                for Y in self.domains[y]:
                    # If the letter at index x_o in word X matches the index y_o in word Y
                    if X[x_o] == Y[y_o]:
                        # Change found to true
                        found = True
                        break
                
                # If we never found an arc to another domain value
                if found == False:
                    # Remove domain value
                    self.domains[x].remove(X)
                    # Change revised to true to signify that we have changed X's domain
                    revised = True


        return revised



    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Begin by creating a queue
        queue = deque(arcs) if arcs is not None else deque()

        # If arcs is none then we have to populate all the arcs
        if arcs is None:
            # Iterate through the variables in the domain
            for var in self.domains:
                # Generate said variables neighbors
                n = self.crossword.neighbors(var)

                # For the variables arc produced by the neighbors set, append the pair arc to the queue
                for arc in n:
                    # Append the (v1, v2) representing an arc between the two to the queue
                    queue.append((var, arc))

        # While the queue is full
        while queue:
            # Assign variables x and y to the first queue item
            x, y = queue.popleft()
            # If we can revise x and y
            if self.revise(x, y):
                # If our variable has no possible domain values
                if not self.domains[x]:
                    return False
                # Go through all of x's other neighbors besides y
                for z in self.crossword.neighbors(x) - {y}:
                    # Append their arc
                    queue.append((z, x))

        return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # Iterate through all the possible variable
        for var in self.crossword.variables:
            # If the variable is not present as a key or their value is not present, return False
            if var not in assignment or assignment[var] is None:
                return False
    
        # If every variable has a string to take on then we return true
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Create a set to check if each answer is distinct
        seen = set()

        # Iterate through all the variables
        for var in assignment:
            # Check the conditions of consistency
            if len(assignment[var]) != var.length:
                return False
            
            if assignment[var] in seen:
                return False
            
            # Iterate through all the neighbors
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                # Assign a variable to the index of both var and neighbor that is shared
                    x, y = self.crossword.overlaps[var, neighbor]
                    if assignment[var][x] != assignment[neighbor][y]:
                        # If not met return false
                        return False
                        
            # If it is met append the current answer to the answer set to be compared against
            seen.add(assignment[var])
                

        # Return true if you get out of the loop without issues
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Create a list to store pairs of (candidate_value, number_ruled_out)
        scored = []

        # For each candidate word that `var` could take
        for val in self.domains[var]:
            # Start a counter for how many neighbor-domain values this `val` would eliminate
            ruled_out = 0

            # Look at every variable that overlaps with `var`
            for neighbor in self.crossword.neighbors(var):
                # Skip neighbors that are already assigned (they don't have a domain to reduce)
                if neighbor in assignment:
                    continue

                # Get the overlap indices: i for `var`'s word, j for `neighbor`'s word
                i, j = self.crossword.overlaps[var, neighbor]

                # For every candidate word of the neighbor
                for nval in self.domains[neighbor]:
                    # If the overlap letters don't match, that neighbor word would be ruled out
                    if val[i] != nval[j]:
                        ruled_out += 1

            # Record the candidate word and how constraining it is
            scored.append((val, ruled_out))

        # Sort candidates so the least-constraining (fewest ruled out) come first
        scored.sort(key=lambda pair: pair[1])

        # Return just the candidate words in the chosen order
        return [val for val, _ in scored]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Candidates = variables not yet assigned
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # MRV: fewest remaining values; tie-break: most (unassigned) neighbors
        return min(
            unassigned,
            key=lambda v: (len(self.domains[v]),
                        -len(self.crossword.neighbors(v) - set(assignment.keys())))
        )


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Success: every variable assigned
        if self.assignment_complete(assignment):
            return assignment

        # Choose a variable to assign next (MRV/degree)
        var = self.select_unassigned_variable(assignment)

        # Try values in least-constraining order
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                # Recurse
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            # Undo and try next value
            del assignment[var]

        # No value worked
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
