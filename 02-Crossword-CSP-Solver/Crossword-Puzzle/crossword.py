class Variable():


    def __init__(self, i, j, direction, length):
        """Create a new variable with starting point, direction, and length."""
        self.i = i
        self.j = j
        self.direction = direction
        self.length = length
        self.cells = []
        for k in range(self.length):
            self.cells.append(
                (self.i + (k if self.direction == "down" else 0),
                 self.j + (k if self.direction == "across" else 0))
            )

    def __hash__(self):
        return hash((self.i, self.j, self.direction, self.length))

    def __eq__(self, other):
        return (
            (self.i == other.i) and
            (self.j == other.j) and
            (self.direction == other.direction) and
            (self.length == other.length))


class Crossword():


    def __init__(self, puzzle_struct, words):
        '''
        init function for the puzzle
        creates all of the attributes for the crossword puzzle object
        initializes structure of the crossword puzzle
        saves the wordlist for the crossword puzzle
        '''
        with open(puzzle_struct) as p:
            puzzle = p.read().splitlines()
            self.height = len(puzzle)
            self.width = len(puzzle[0])

            self.struct = []

                
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    if j >= len(puzzle[i]):
                        row.append(False) # set to false if the square is blocked
                    elif puzzle[i][j] == "_":
                        row.append(True) # set to true if square is free
                    else:
                        row.append(False)
                self.struct.append(row)

        # now we save word profile
        with open(words) as w: self.words = set(w.read().upper().splitlines())


        self.create_var_set()
        self.find_overlaps()

    def create_var_set(self):

        '''
        This functions add/creates all of the variables for the CSP problem
        For this CSP, I decided to treat the words as variables. Such as x
        across or y down.
        '''
        self.variables = set()
        for i in range(self.height):
            for j in range(self.width):

                # check for vertical words (variables)
                initial = (self.struct[i][j] and (i == 0 or not self.struct[i - 1][j]))
                if initial:
                    length = 1
                    k = i+1
                    while k < self.height and self.struct[k][j]:
                        length+=1
                        k+=1
                    if length > 1:
                        self.variables.add(Variable(
                            i=i, j=j,
                            direction="down",
                            length=length
                        ))
                # check for horizantal words (variables)
                initial = (self.struct[i][j] and (j == 0 or not self.struct[i][j-1]))
                if initial:
                    length = 1
                    k = j+1
                    while k < self.width and self.struct[i][k]:
                        length+=1
                        k+=1
                    if length > 1:
                        self.variables.add(Variable(
                            i=i, j=j,
                            direction="across",
                            length=length
                        ))
    


    def print(self):
        '''
        Function that prints the current structure of the crossword puzzle
        '''
        for row in self.struct:
            for value in row:
                if value == False: print("▢", end=" ")
                else: print("_", end=" ")
            print("\n")

    def find_overlaps(self):
        '''
        This function finds all of the overlapping words 
        of the crossword puzzle
        '''
        self.overlaps=dict()

        for v1 in self.variables:
            for v2 in self.variables:
                if v1 != v2:
                    cells1, cells2 = v1.cells, v2.cells
                    intersection = set(cells1).intersection(cells2)
                    if not intersection: self.overlaps[v1, v2] = None
                    else:
                        intersection = intersection.pop()
                        self.overlaps[v1, v2] = (
                            cells1.index(intersection),
                            cells2.index(intersection)
                        )

    def neighbours(self, variable):
        '''
        Finds all neighbours of given word
        '''
        return set(
            v for v in self.variables
            if v != variable and self.overlaps[v, variable]
        )