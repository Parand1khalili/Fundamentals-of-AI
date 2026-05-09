import sys

from crossword import *


class Creator():

    def __init__(self, crossword, heuristic):
        '''
        initializes new crossword to inherit from crossword class
        also initializes domain for each variable
        '''
        self.crossword = crossword
        self.heuristic = heuristic
        self.domains = {}
        for var in self.crossword.variables:
            self.domains[var] = self.crossword.words.copy()


    def is_domain_consistent(self):
        """Enforce node consistency by removing words whose length != variable length."""
        # DONE: Implement node consistency check.
        # Iterate over all variables in the puzzle
        for var in self.domains:
            # Create a set of words we need to remove to avoid modifying the set while iterating
            words_to_remove = set()
            
            for word in self.domains[var]:
                # If the word's length doesn't match the variable's required length, mark it
                if len(word) != var.length:
                    words_to_remove.add(word)
            
            # Now, remove the invalid words from the variable's domain
            if words_to_remove:
                self.domains[var] -= words_to_remove



    def revise(self, x, y):
        """Revise domain of x to enforce consistency with y.
        Remove any word from domain[x] that has no matching word in domain[y].
        """
        # DONE: Implement revise function from CSP algorithm
        revised = False
        
        # First find out where these two variables overlap
        overlap = self.crossword.overlaps.get((x, y))
        
        # If they don't overlap, no constraint to check
        if overlap is None:
            return False
        
        i, j = overlap
        words_to_remove = set()

        # Check each word in x's domain
        for word_x in self.domains[x]:
            found_match = False
            
            # Look for at least one compatible word in y's domain
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    found_match = True
                    break
            
            # If no compatible word was found in y, word_x cannot be part of the solution
            if not found_match:
                words_to_remove.add(word_x)
                revised = True
        
        # Apply the changes to the domain
        self.domains[x] -= words_to_remove
        return revised



    def pre_process_ac3(self):
        arcs = list()
        for x in self.domains:
            for y in self.crossword.neighbours(x):
                arcs.append((x, y))
        return arcs


    def ac3(self, arcs = None):
        """Implement AC-3 algorithm to enforce arc consistency.
        Should return True if successful; False if a domain becomes empty.
        """
        # DONE: Implement AC-3 algorithm.
        # If no specific arcs provided, start with all possible arcs in the queue
        if arcs is None:
            queue = self.pre_process_ac3()
        else:
            queue = list(arcs)
        
        while queue:
            # Pop the first arc to process
            x, y = queue.pop(0)
            
            # Try to revise x's domain based on y
            if self.revise(x, y):
                # If x's domain became empty, the problem is unsolvable
                if len(self.domains[x]) == 0:
                    return False
                
                # Since x changed, we need to re-check all its neighbors (except y)
                for neighbor in self.crossword.neighbours(x):
                    if neighbor != y:
                        queue.append((neighbor, x))
        
        return True



    def is_assign_consistent(self, assignment):
        used = set()
        for v in assignment:
            if assignment[v] not in used:
                used.add(assignment[v])
            else:
                return False
            for n in self.crossword.neighbours(v):
                if n in assignment:
                    i, j = self.crossword.overlaps[v, n]
                    if assignment[v][i] != assignment[n][j]: return False
        return True

    def is_solved(self, assignment):
        '''
        Helper function to show whether the crossword is complete 
        '''
        return not bool(self.crossword.variables - set(assignment))
    

    def select_unassigned_var(self, assignment, heuristic):
        """Select an unassigned variable using:
        - MRV (minimum remaining values)
        - If heuristic=True, combine with degree heuristic.
        """
        # DONE : Implement MRV (and optionally degree heuristic).
        # Get all variables that haven't been assigned a value yet
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        
        # Helper to calculate domain size (MRV)
        def domain_size(var):
            return len(self.domains[var])
        
        # Helper to calculate degree (number of neighbors)
        def degree(var):
            return len(self.crossword.neighbours(var))

        # If heuristic is enabled, we use MRV primary, Degree secondary
        if self.heuristic:
            # Sort by domain size (asc), then by degree (desc) as tie-breaker
            # Note: usually degree is used on unassigned neighbors, but simple degree is often enough
            unassigned.sort(key=lambda var: (domain_size(var), -degree(var)))
        else:
            # Just standard MRV
            unassigned.sort(key=domain_size)

        # Return the best candidate
        return unassigned[0]
    
    
    def order_domain_values(self, var, assignment):
        """Return domain values for `var` ordered by Least Constraining Value (LCV).

        The LCV heuristic prefers values that eliminate the fewest options
        for neighboring variables.
        """
        # DONE: Implement LCV heuristic.
        # Helper to count how many values a choice rules out
        def count_constraints(value):
            count = 0
            for neighbor in self.crossword.neighbours(var):
                # We only care about neighbors that are not yet assigned
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    for neighbor_word in self.domains[neighbor]:
                        # If the words conflict at the intersection, it's a constraint
                        if value[i] != neighbor_word[j]:
                            count += 1
            return count

        # Sort the domain values based on the number of constraints they cause (ascending)
        # Fewer constraints = better value to try first
        return sorted(self.domains[var], key=count_constraints) # comment this for without lcv
        #return list(self.domains[var]) #use this instead


    def backtrack(self, assignment):
        """Implement recursive backtracking search.
        Should return a complete assignment if successful, else None.
        """
        # DONE: Implement backtracking algorithm with consistency checks.
        # Base case: check if the assignment is complete
        if self.is_solved(assignment):
            return assignment
        
        # Select the next variable to assign
        var = self.select_unassigned_var(assignment, self.heuristic)
        
        # Iterate through values ordered by LCV
        for value in self.order_domain_values(var, assignment):
            # Check if assigning this value is consistent with current assignment
            # We tentatively add it to check consistency
            new_assignment = assignment.copy()
            new_assignment[var] = value
            
            if self.is_assign_consistent(new_assignment):
                # If consistent, proceed deeper into the recursion
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
            
            # If we reach here, the value didn't work out (backtracking happens implicitly by loop)
        
        # If no value worked for this variable, return failure
        return None
    
    
    def solve(self):
        """Solve the crossword CSP by enforcing consistency and using backtracking search."""
        self.is_domain_consistent()
        arcs = self.pre_process_ac3()
        self.ac3(arcs)
        return self.backtrack(dict())
