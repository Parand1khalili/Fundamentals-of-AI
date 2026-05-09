"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random


class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Heuristic 1: Improved Score (Aggressive)
    This heuristic simply calculates the difference between my available moves
    and the opponent's available moves. It encourages blocking the opponent aggressively.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game.

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    
    # Maximize my moves, minimize their moves
    return float(own_moves - opp_moves)

def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Heuristic 2: Center Control
    This heuristic values moves that keep the player closer to the center of the board.
    The center offers more mobility in the future (usually).
    We combine it with the number of moves to ensure we don't get stuck.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game.

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # available moves
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    
    # distance from center
    w, h = game.width / 2., game.height / 2.
    y, x = game.get_player_location(player)
    dist_from_center = float((h - y)**2 + (w - x)**2)
    
    # We want more moves + be closer to center 
    # We subtract distance (weighted slightly) to penalize being far from center
    return float(own_moves - opp_moves) - (dist_from_center * 0.1)

def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Heuristic 3: Weighted Mobility (Advanced)
    This heuristic changes strategy based on the game stage.
    - Early game: Occupy center (mobility is high anyway).
    - Mid/Late game: Focus purely on restricting opponent (mobility difference).
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game.

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    
    # Count empty spaces -> estimate game stage
    empty_spaces = len(game.get_blank_spaces())
    total_spaces = game.width * game.height
    
    # If more than 50% of board is empty, it's early game
    if empty_spaces > total_spaces / 2:
        # In early game, prioritize own mobility more to build a strong position
        return float(own_moves - (2 * opp_moves))
    else:
        # In late game, strictly maximize the difference to corner the opponent
        return float(own_moves - opp_moves)

class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            You MUST use the `self.score()` method for board evaluation
            to pass the project tests; you cannot call any other evaluation
            function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        # Helper function for Max-Value
        def max_value(game_state, current_depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            
            # Terminal check or depth limit reached
            if current_depth == 0 or not game_state.get_legal_moves():
                return self.score(game_state, self)
            
            v = float("-inf")
            for move in game_state.get_legal_moves():
                v = max(v, min_value(game_state.forecast_move(move), current_depth - 1))
            return v

        # Helper function for Min-Value
        def min_value(game_state, current_depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            
            # Terminal check or depth limit reached
            if current_depth == 0 or not game_state.get_legal_moves():
                return self.score(game_state, self)
            
            v = float("inf")
            for move in game_state.get_legal_moves():
                v = min(v, max_value(game_state.forecast_move(move), current_depth - 1))
            return v

        # Body of Minimax Decision
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)
        
        # Start the search from the root (Max player)
        # return the move -> expand the first level manually
        best_score = float("-inf")
        best_move = legal_moves[0]
        
        for move in legal_moves:
            # The next level will be Min's turn
            score = min_value(game.forecast_move(move), depth - 1)
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move

class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        best_move = (-1, -1)
        legal_moves = game.get_legal_moves()
        
        if not legal_moves:
            return best_move
            
        # Initialize with a random move just in case we time out immediately
        best_move = legal_moves[0]

        try:
            # Iterative Deepening: Start from depth 1 and increase
            # go up to infinity, (SearchTimeout to stop us)
            depth = 1
            while True:
                # Call alphabeta for the current depth
                move = self.alphabeta(game, depth)
                
                # If we completed the search without timeout, update best move
                best_move = move
                
                # Optimization: If we found a winning move (score is inf), no need to search deeper
                # But since alphabeta returns move, we can't easily check score here without re-evaluating.
                # For simplicity, we just keep deepening until timeout.
                
                depth += 1

        except SearchTimeout:
            # When timeout happens, we just return the best move found in the LAST COMPLETED depth
            pass

        return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            You MUST use the `self.score()` method for board evaluation
            to pass the project tests; you cannot call any other evaluation
            function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        # Helper function for Max-Value with Pruning
        def max_value(game_state, current_depth, a, b):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            
            if current_depth == 0 or not game_state.get_legal_moves():
                return self.score(game_state, self)
            
            v = float("-inf")
            for move in game_state.get_legal_moves():
                v = max(v, min_value(game_state.forecast_move(move), current_depth - 1, a, b))
                if v >= b:
                    return v  # Pruning
                a = max(a, v)
            return v

        # Helper function for Min-Value with Pruning
        def min_value(game_state, current_depth, a, b):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            
            if current_depth == 0 or not game_state.get_legal_moves():
                return self.score(game_state, self)
            
            v = float("inf")
            for move in game_state.get_legal_moves():
                v = min(v, max_value(game_state.forecast_move(move), current_depth - 1, a, b))
                if v <= a:
                    return v  # Pruning
                b = min(b, v)
            return v

        # Body of Alpha-Beta Search
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)
        
        best_score = float("-inf")
        best_move = legal_moves[0]
        
        # Expand root node manually to return the move
        for move in legal_moves:
            score = min_value(game.forecast_move(move), depth - 1, alpha, beta)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            # Update alpha for the root level as well
            alpha = max(alpha, best_score)
                
        return best_move


class ExpectimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited Expectimax
    search.

    Unlike Minimax or AlphaBeta, this agent assumes that the opponent acts
    stochastically (i.e., chooses moves uniformly at random) rather than
    optimally. Therefore, the Expectimax algorithm computes the expected
    value of successor states instead of the minimum value.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        depth-limited Expectimax search instead of Minimax or AlphaBeta.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        best_move = (-1, -1)
        
        try:
            # Similar to Iterative Deepening, but using Expectimax logic
            depth = 1
            while True:
                best_move = self.expectimax(game, depth)
                depth += 1
                
        except SearchTimeout:
            pass
            
        return best_move

    def expectimax(self, game, depth):
        """Implement depth-limited Expectimax search as described in
        the lectures and AIMA text.

        This should be a modified version of the Expectimax-Decision
        algorithm described in standard AI textbooks. Expectimax evaluates
        the expected value of successor states under the assumption that
        the opponent acts randomly rather than adversarially.

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state.

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting.

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves.

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to remain consistent with project testing.

            (2) Unlike Minimax or AlphaBeta, this algorithm computes expected
                values instead of min or max values at opponent layers.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        # Helper for Max-Value (Player's turn)
        def max_value(game_state, current_depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            
            if current_depth == 0 or not game_state.get_legal_moves():
                return self.score(game_state, self)
            
            v = float("-inf")
            for move in game_state.get_legal_moves():
                v = max(v, exp_value(game_state.forecast_move(move), current_depth - 1))
            return v

        # Helper for Exp-Value (Opponent's turn - Random behavior)
        def exp_value(game_state, current_depth):
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            
            legal_moves = game_state.get_legal_moves()
            if current_depth == 0 or not legal_moves:
                return self.score(game_state, self)
            
            # Calculate average score (Uniform probability distribution)
            total_score = 0
            for move in legal_moves:
                total_score += max_value(game_state.forecast_move(move), current_depth - 1)
            
            return total_score / len(legal_moves)

        # Body of Expectimax Decision
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return (-1, -1)
        
        best_score = float("-inf")
        best_move = legal_moves[0]
        
        for move in legal_moves:
            score = exp_value(game.forecast_move(move), depth - 1)
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move
