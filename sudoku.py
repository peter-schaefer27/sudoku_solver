# Created using adapted source code from Harvard's CS50 AI course on EdX

import sys

class Node():
    def __init__(self, state, parent, action, possible_actions_count = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.possible_actions_count = possible_actions_count


class Frontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            min_node = min(self.frontier, key=lambda node: node.possible_actions_count)
            self.frontier.remove(min_node)
            return min_node


class Puzzle():

    def __init__(self, filename):

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Confirm size of board
        rows = contents.splitlines()
        if len(rows) != 9:
            raise Exception("puzzle must be 9 rows")
        
        columns = [''.join(row[i] for row in rows) for i in range(9)]
        if len(columns) != 9:
            raise Exception("puzzle must be 9 columns")
        
        # Validate characters
        valid_chars = set("1234567890")
        for row in rows:
            if any(char not in valid_chars for char in row):
                raise Exception("invalid character in puzzle")
            
        # Store puzzle as list of lists
        self.puzzle = []
        for row in rows:
            self.puzzle.append([int(char) for char in row]) 
        
        self.solution = None

    def to_state(self):
        """
        Convert puzzle to a state representation (tuple of tuples)
        """
        return tuple(tuple(row) for row in self.puzzle)
    
    def __hash__(self):
        return hash(self.to_state())
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.to_state() == other.to_state()


    def logic_advance(self, state):
        '''
        Advance the puzzle using simple logic: if a cell has only one possible value, fill it in
        '''
        puzzle_list = [list(row) for row in state]  # convert tuple of tuples to list of lists
        changes_made = True

        while changes_made:
            changes_made = False
            for i in range(9):
                for j in range(9):
                    if puzzle_list[i][j] == 0:
                        possible = set(range(1, 10))
                        # Remove values in same row
                        for val in puzzle_list[i]:
                            possible.discard(val)
                        # Remove values in same column
                        for k in range(9):
                            possible.discard(puzzle_list[k][j])
                        # Remove values in same 3x3 box
                        box_row_start = (i // 3) * 3
                        box_col_start = (j // 3) * 3
                        for r in range(box_row_start, box_row_start + 3):
                            for c in range(box_col_start, box_col_start + 3):
                                possible.discard(puzzle_list[r][c])
                        # If only one candidate, fill it
                        if len(possible) == 1:
                            puzzle_list[i][j] = possible.pop()
                            changes_made = True
        
        return tuple(tuple(row) for row in puzzle_list)
    
    def possible_guesses(self, state):
        """
        Given a state, return a list of (action, state) pairs for possible guesses
        Action is a tuple (row, col, value)
        State is the new puzzle state after making the guess
        """
        puzzle_list = [list(row) for row in state]
        for i in range(9):
            for j in range(9):
                if puzzle_list[i][j] == 0:
                    possible = set(range(1, 10))
                    # Remove values in same row
                    for val in puzzle_list[i]:
                        possible.discard(val)
                    # Remove values in same column
                    for k in range(9):
                        possible.discard(puzzle_list[k][j])
                    # Remove values in same 3x3 box
                    box_row_start = (i // 3) * 3
                    box_col_start = (j // 3) * 3
                    for r in range(box_row_start, box_row_start + 3):
                        for c in range(box_col_start, box_col_start + 3):
                            possible.discard(puzzle_list[r][c])
                    # Generate new states for each possible value
                    results = []
                    for val in possible:
                        new_puzzle = [list(row) for row in puzzle_list]
                        new_puzzle[i][j] = val
                        new_state = tuple(tuple(row) for row in new_puzzle)
                        action = (i, j, val)
                        results.append((action, new_state))
                    return results
        return []
    
    def solve(self):
        """
        Solve puzzle using depth-first search
        """
        # Initialize frontier to just the starting position
        start = Node(self.to_state(), None, None)
        frontier = Frontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        while True:

            # If nothing left in frontier, then no solution
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()

            # If node is the goal, then we have a solution
            if all(all(cell != 0 for cell in row) for row in node.state):
                # Convert state back to puzzle format
                self.solution = [list(row) for row in node.state]
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add new nodes to frontier
            for action, state in self.possible_guesses(node.state):
                state = self.logic_advance(state)
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state, node, action, len(self.possible_guesses(state)))
                    frontier.add(child)
    
    
    def print_puzzle(self):
        """
        Print the puzzle in a readable format
        """
        if self.solution:
            puzzle_to_print = self.solution
        else:
            puzzle_to_print = self.puzzle
        
        lines = []
        for i, row in enumerate(puzzle_to_print):
            if i % 3 == 0 and i != 0:
                lines.append("- - - + - - - + - - -")
            line = ""
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    line += "| "
                line += str(val) + " "
            lines.append(line.strip())
        return "\n".join(lines)


if len(sys.argv) != 2:
    sys.exit("Usage: python sudoku.py puzzle.txt")

puzzle = Puzzle(sys.argv[1])
puzzle.solve()
print()
print()
print(puzzle.print_puzzle())
print(f"\nStates explored: {len(puzzle.explored)}\n")