import os
import sys
import time
import pygame
import pygame.gfxdraw as gfx
from dataclasses import dataclass
from typing import List, Tuple, Set, FrozenSet, Dict, Optional, Iterable
from collections import deque
import logging
import heapq
from typing import List, Tuple, Dict


logging.basicConfig(level=logging.INFO)

 
TILE = 64
FPS = 90
FONT_NAME = None
MARGIN = 16
BANNER_H = 56

COLORS = {
    "bg": (44, 44, 46),
    "panel": (250, 250, 252),
    "panel_border": (220, 222, 226),
    "wall": (110, 110, 110),
    "floor": (238, 240, 243),
    "goal": (255, 204, 0),
    "box": (181, 101, 29),
    "box_on_goal": (120, 170, 40),
    "player": (66, 135, 245),
    "grid": (210, 210, 210),
    "text": (32, 33, 36),
    "shadow": (0, 0, 0),
    "apple": (60, 180, 75),
    "apple_leaf": (40, 120, 55),
    "poison": (200, 60, 60),
    "poison_core": (140, 20, 20),
}

 
SAMPLE_LEVELS = [
    [
        "#####",
        "# @ #",
        "# $p#",
        "# .a#",
        "#####",
    ],
    [
        "######",
        "# .. #",
        "# $$a#",
        "#  @ #",
        "######",
    ],
    [
        "########",
        "# .  . #",
        "# $$   #",
        "#  # p #",
        "#  @   #",
        "########",
    ],
    [
        "###########",
        "#   #     #",
        "# # # ### #",
        "# $   $   #",
        "### # # # #",
        "#  . . .  #",
        "#   $   # #",
        "# @   #   #",
        "###########",
    ],
    [
        "############",
        "#    #     #",
        "# $$ # $$  #",
        "#    #   ###",
        "###  ###   #",
        "# .  .     #",
        "#    #   # #",
        "#  @   p a #",
        "# .     .  #",
        "############",
    ],
    [
        "###############",
        "#   ###   #   #",
        "# $   # $   $ #",
        "## #  #  # # ##",
        "#   . . . .   #",
        "#  ### # ###  #",
        "# @    $    p #",
        "#   ### # ### #",
        "#   a       ###",
        "###############",
    ],
]

 
WALL = "#"
FLOOR = " "
PLAYER = "@"
BOX = "$"
GOAL = "."
BOX_ON_GOAL = "*"
PLAYER_ON_GOAL = "+"
APPLE_CHARS = ("a", "A")
POISON_CHARS = ("p", "P")

 
ACTIONS = ["U", "D", "L", "R"]
DIRS = {
    "U": (0, -1),
    "D": (0, 1),
    "L": (-1, 0),
    "R": (1, 0)
}


 
@dataclass(frozen=True)
class State:
    player: Tuple[int, int]
    boxes: FrozenSet[Tuple[int, int]]

    def __hash__(self):
        return hash((self.player, self.boxes))

    def __lt__(self, other):
        # players
        if self.player != other.player:
            return self.player < other.player
        # boxes
        return self.boxes < other.boxes        

class SokobanProblem:
    def __init__(self, grid: List[str], use_deadlocks: bool = False):
        self.w = max(len(row) for row in grid)
        self.h = len(grid)
        self.walls: Set[Tuple[int,int]] = set()
        self.goals: Set[Tuple[int,int]] = set()
        self.apples_initial: Set[Tuple[int,int]] = set()
        self.poisons_initial: Set[Tuple[int,int]] = set()
        #self.visited: set[State] = set()  # مجموعه برای ذخیره وضعیت‌های بازدید شده
        #self.deadlocks: WeakSet[State] = WeakSet()  # WeakSet برای بن‌بست‌ها
        player = None
        boxes: Set[Tuple[int,int]] = set()
        
        for y, row in enumerate(grid):
            for x, ch in enumerate(row.ljust(self.w)):
                if ch == WALL:
                    self.walls.add((x, y))
                elif ch == GOAL:
                    self.goals.add((x, y))
                elif ch in APPLE_CHARS:
                    self.apples_initial.add((x, y))
                elif ch in POISON_CHARS:
                    self.poisons_initial.add((x, y))
                elif ch == BOX:
                    boxes.add((x, y))
                elif ch == PLAYER:
                    player = (x, y)
                elif ch == BOX_ON_GOAL:
                    boxes.add((x, y))
                    self.goals.add((x, y))
                elif ch == PLAYER_ON_GOAL:
                    player = (x, y)
                    self.goals.add((x, y))
        if player is None:
            raise ValueError("Level missing a player '@' or '+'.")
        self.initial = State(player=player, boxes=frozenset(boxes))
        self.use_deadlocks = use_deadlocks

    
    def is_goal(self, s: State) -> bool:
        return set(s.boxes) == self.goals

    def in_bounds(self, pos: Tuple[int,int]) -> bool:
        x, y = pos
        return 0 <= x < self.w and 0 <= y < self.h

    def is_free(self, s: State, pos: Tuple[int,int]) -> bool:
        return pos not in self.walls and pos not in s.boxes

    def successors(self, s: State):
        px, py = s.player
        boxes = set(s.boxes)
        
        for a in ACTIONS:
            dx, dy = DIRS[a]
            np = (px + dx, py + dy)
            
            if self.is_free(s, np):
                yield a, State(np, frozenset(boxes)), 1.0
                continue
            
            if np in boxes:
                after = (np[0] + dx, np[1] + dy)
                
                if self.in_bounds(after) and (after not in self.walls) and (after not in boxes):
                    if self.use_deadlocks and self._is_simple_corner_deadlock(after):
                        continue
                    new_boxes = set(boxes)
                    new_boxes.remove(np)
                    new_boxes.add(after)
                    
                    yield a, State(np, frozenset(new_boxes)), 5.0


    def cost(self, s: State, a: str, sp: State) -> float:
        return 5.0 if s.boxes != sp.boxes else 1.0


    
    def _is_simple_corner_deadlock(self, pos: Tuple[int,int]) -> bool:
        if pos in self.goals:
            return False
        x, y = pos
        up = (x, y-1) in self.walls
        down = (x, y+1) in self.walls
        left = (x-1, y) in self.walls
        right = (x+1, y) in self.walls
        return (up and left) or (up and right) or (down and left) or (down and right)
    

def dfs_search(problem: SokobanProblem, max_depth=300):
    # Stack for DFS, starting with the initial state
    stack = [(problem.initial, [])]
    visited = set()  # Keep track of visited states to avoid loops
    deadlocks = set() 
    
    parent = {problem.initial: (None, None)}  

    logging.info("Starting DFS...")

    while stack:
        state, path = stack.pop()

        # Goal check
        if problem.is_goal(state):
            logging.info("Goal found")
            actions = _reconstruct_path(parent, state)
            print("Path to goal:", actions)  # print
            return actions, {'expanded': len(visited)}

        # Skip if already visited or if it's a deadlock
        if state in visited or state in deadlocks:
            continue

        visited.add(state)

        # Generate successors and add them to the stack
        for action, successor, _ in problem.successors(state):
            if successor not in visited and successor not in deadlocks:
                if _is_deadlock(successor, problem):  # Check if it's a deadlock
                    deadlocks.add(successor)
                    continue
                parent[successor] = (state, action)  # به‌روزرسانی parent
                if len(path) < max_depth:  # Limiting depth
                    stack.append((successor, path + [action]))

    logging.warning("No solution found")
    return [], {'expanded': len(visited)}




def bfs_search(problem: SokobanProblem, max_queue_size=250):
    queue = deque([(problem.initial, [])]) 
    visited = set() 
    deadlocks = set()  

    parent = {problem.initial: (None, None)}  

    logging.info("Starting BFS ...")

    while queue:
        if len(queue) > max_queue_size:
            max_queue_size = max(max_queue_size, len(queue) * 2)  

        current_state, path = queue.popleft()

        # Goal check
        if problem.is_goal(current_state):
            logging.info("Goal found")
            return path, {"expanded": len(visited)}

        # Skip if already visited or if it's a deadlock
        if current_state in visited or current_state in deadlocks:
            continue

        visited.add(current_state)

        for action, successor, _ in problem.successors(current_state):
            if successor not in visited and successor not in deadlocks:
                if successor not in parent:
                    parent[successor] = (current_state, action)
                
                if _is_deadlock(successor, problem):  
                    deadlocks.add(successor)
                    continue
                queue.append((successor, path + [action])) 

    logging.warning("No solution found")
    return [], {"expanded": len(visited)}



def ucs_search(problem: SokobanProblem):
    # Priority queue: stores tuples of (cost, state)
    frontier = []
    heapq.heappush(frontier, (0, problem.initial))  # (cost, state)

    explored = set()  # Set of states we have fully explored
    cost_so_far = {problem.initial: 0}  # Cost to reach each state
    parent = {problem.initial: (None, None)}  # Parent states and actions

    while frontier:
        cost, current_state = heapq.heappop(frontier)

        # If the current state is the goal, return the reconstructed path
        if problem.is_goal(current_state):
            logging.info("Goal found")
            actions = _reconstruct_path(parent, current_state)
            print("Path to goal:", actions)  # Print the path in the terminal
            return actions, {"expanded": len(explored)}

        # If this state is in explored but we find a cheaper way to it, update it
        if current_state in explored:
            continue

        explored.add(current_state)

        # Generate successors (next possible states)
        for action, successor, move_cost in problem.successors(current_state):
            # Check if the successor is a deadlock state
            if _is_deadlock(successor, problem):
                continue  # Skip deadlock states

            new_cost = cost + move_cost

            # Only consider successors if they are cheaper or unexplored
            if successor not in cost_so_far or new_cost < cost_so_far[successor]:
                cost_so_far[successor] = new_cost
                parent[successor] = (current_state, action)  # Update parent
                heapq.heappush(frontier, (new_cost, successor))

    logging.warning("No solution found")
    return [], {"expanded": len(explored)}


def greedy_search(problem: SokobanProblem):
    start_state = problem.initial
    pq = [(heuristic_function(start_state, problem), start_state, [])]  
    visited = set() 
    deadlocks = set() 

    parent = {start_state: (None, None)}  

    logging.info("Starting Greedy Search...")

    while pq:
        _, state, path = heapq.heappop(pq)

        # Goal check
        if problem.is_goal(state):
            logging.info("Goal state found!")
            actions = _reconstruct_path(parent, state)
            print("Path to goal:", actions) 
            return actions, {'expanded': len(visited)}

        # Skip if already visited or if it's a deadlock
        if state in visited or state in deadlocks:
            continue

        visited.add(state)

        for action, successor, _ in problem.successors(state):
            if _is_deadlock(successor, problem):
                deadlocks.add(successor)
                continue

            heuristic_cost = heuristic_function(successor, problem)

            # If this successor has not been visited, add to priority queue
            if successor not in visited:
                parent[successor] = (state, action)  # update parent
                heapq.heappush(pq, (heuristic_cost, successor, path + [action]))

    logging.warning("No solution found")
    return [], {'expanded': len(visited)}


def astar_search(problem: SokobanProblem):
    # Priority queue stores tuples (f_cost, g_cost, state, path)
    start_state = problem.initial
    pq = [(0 + heuristic_function(start_state, problem), 0, start_state, [])]  # f_cost, g_cost, state, path_to_state
    
    # Sets to keep track of visited states and their best g_cost
    visited = set()
    best_g_cost = {start_state: 0}  # Track the best g_cost found for each state
    
    # Deadlock handling
    deadlocks = set()
    
    # Dictionary to track parent states and the action taken to reach them
    parent = {start_state: (None, None)}  # Stores (parent_state, action_taken)
    
    logging.info("Starting A* search...")

    while pq:
        f_cost, g_cost, state, path = heapq.heappop(pq)

        # Skip deadlock states
        if state in deadlocks:
            continue
        
        # If goal state is reached, return the path
        if problem.is_goal(state):
            logging.info("Goal state found!")
            actions = _reconstruct_path(parent, state)
            print("Path to goal:", actions)  # چاپ مسیر در ترمینال
            return actions, {'expanded': len(visited)}

        # Skip if already visited or if a better g_cost has been found
        if state in visited and g_cost >= best_g_cost.get(state, float('inf')):
            continue

        # Mark this state as visited and record the best g_cost
        visited.add(state)
        best_g_cost[state] = g_cost

        # Generate successors (next possible states)
        for action, successor, step_cost in problem.successors(state):
            # Skip deadlock states
            if _is_deadlock(successor, problem):
                deadlocks.add(successor)
                continue
            
            # Calculate g_cost (cost to reach the successor)
            new_g_cost = g_cost + step_cost
            h_cost = heuristic_function(successor, problem)  # Heuristic (Manhattan Distance)
            f_cost = new_g_cost + h_cost  # Total cost (f_cost = g_cost + h_cost)

            # If this path is better (or the state has not been visited yet), push it to the priority queue
            if successor not in visited or new_g_cost < best_g_cost.get(successor, float('inf')):
                # Update the parent for the successor
                parent[successor] = (state, action)
                heapq.heappush(pq, (f_cost, new_g_cost, successor, path + [action]))

    logging.warning("No solution found")
    return [], {'expanded': len(visited)}



def heuristic_function(state: State, problem: SokobanProblem) -> int:
    # Manhattan distance for each box to the closest goal
    goal_distances = [abs(goal[0] - state.player[0]) + abs(goal[1] - state.player[1]) for goal in problem.goals]
    min_goal_distance = min(goal_distances) if goal_distances else 0

    player_box_distances = [abs(state.player[0] - box[0]) + abs(state.player[1] - box[1]) for box in state.boxes]
    min_player_box_distance = min(player_box_distances) if player_box_distances else 0


    box_distances = []
    for box in state.boxes:
        box_goal_distances = [abs(goal[0] - box[0]) + abs(goal[1] - box[1]) for goal in problem.goals]
        min_box_distance = min(box_goal_distances) if box_goal_distances else 0
        box_distances.append(min_box_distance)
    
    boxes_on_goal = sum(1 for box in state.boxes if box in problem.goals)
    moveable_box_cost = 0
    for box in state.boxes:
        if problem._is_simple_corner_deadlock(box):
            moveable_box_cost += 10 

    deadlock_cost = 0
    for box in state.boxes:
        if problem._is_simple_corner_deadlock(box):
            deadlock_cost += 100
    
    subgoal_cost = 0
    if boxes_on_goal < len(state.boxes):
        subgoal_cost = 5 * (len(state.boxes) - boxes_on_goal)
    
    heuristic_value = min_goal_distance + sum(box_distances) + deadlock_cost + moveable_box_cost + subgoal_cost + min_player_box_distance
    return heuristic_value


def _is_deadlock(state: State, problem: SokobanProblem) -> bool:
    #Checks if a given state is a deadlock by checking if any box is stuck in a corner.
    for box in state.boxes:
        if problem._is_simple_corner_deadlock(box):
            return True
    return False


def _reconstruct_path(parent: Dict[State, Tuple[Optional[State], Optional[str]]], goal: State) -> List[str]:
    actions: List[str] = []
    s = goal
    while True:
        ps, a = parent[s]
        if ps is None:
            break
        actions.append(a)
        s = ps
    actions.reverse()
    return actions

 
ALGO_NAMES = ["dfs", "bfs", "ucs", "greedy", "astar"]

class Solver:
    def __init__(self, problem: SokobanProblem):
        self.problem = problem
        self.plan: List[str] = []
        self.stats: Dict[str, float] = {}
        self.status_msg: str = ""

    def compute(self, algo_name: str) -> None:
        f = {
            "dfs": dfs_search,
            "bfs": bfs_search,
            "ucs": ucs_search,
            "greedy": greedy_search,
            "astar": astar_search,
        }[algo_name]
        t0 = time.perf_counter()
        actions, stats = f(self.problem)
        t1 = time.perf_counter()
        self.plan = actions
        stats = dict(stats or {})
        elapsed_ms = max(1, int(round((t1 - t0) * 1000)))
        stats["time_ms"] = elapsed_ms
        stats.setdefault("time_s", round(t1 - t0, 3))
        stats.setdefault("cost", len(actions))
        self.stats = stats
        self.status_msg = (
            f"Solved with {algo_name.upper()}: {len(actions)} steps, "
            f"{stats.get('expanded','?')} expanded, {elapsed_ms} ms"
        )

 
class Game:
    def __init__(self, level_idx: int = 0, use_deadlocks: bool = True):
        self.level_idx = level_idx % len(SAMPLE_LEVELS)
        self.grid = SAMPLE_LEVELS[self.level_idx]
        self.problem = SokobanProblem(self.grid, use_deadlocks=use_deadlocks)
        self.state = self.problem.initial
        self.history: List[str] = []
        self.algo_idx = 1
        self.solver: Optional[Solver] = None
        self.font = None
        self.info_font = None
        
        self.anim = None
        self.plan_autoplay = False
        
        self.level_complete: bool = False
        self.completion_cost: Optional[int] = None
        
        self.box_img = None
        self.box_img_scaled = None
        try:
            box_path = os.path.join(os.path.dirname(__file__), "pics/box.png")
            self.box_img = pygame.image.load(box_path).convert_alpha()
            self.box_img_scaled = pygame.transform.smoothscale(self.box_img, (TILE - 12, TILE - 12))
        except Exception:
            self.box_img = None
            self.box_img_scaled = None
        
        self.player_imgs = {}
        self.player_imgs_scaled = {}
        self.facing = "D"
        try:
            root = os.path.dirname(__file__)
            files = {"U": "pics/up.png", "D": "pics/down.png", "L": "pics/left.png", "R": "pics/right.png"}
            for k, fname in files.items():
                img = pygame.image.load(os.path.join(root, fname)).convert_alpha()
                self.player_imgs[k] = img
                self.player_imgs_scaled[k] = pygame.transform.smoothscale(img, (TILE - 12, TILE - 12))
        except Exception:
            
            self.player_imgs = {}
            self.player_imgs_scaled = {}
        
        self.apples: Set[Tuple[int,int]] = set(self.problem.apples_initial)
        self.apple_buff_steps: int = 0
        
        self.poisons: Set[Tuple[int,int]] = set(self.problem.poisons_initial)
        self.poison_active: bool = False
        
        self.apple_img = None
        self.apple_img_scaled = None
        self.poison_img = None
        self.poison_img_scaled = None
        try:
            root = os.path.dirname(__file__)
            ap = os.path.join(root, "pics/apple.png")
            pp = os.path.join(root, "pics/poison.png")
            if os.path.exists(ap):
                self.apple_img = pygame.image.load(ap).convert_alpha()
                small = max(8, int(TILE * 0.4))
                self.apple_img_scaled = pygame.transform.smoothscale(self.apple_img, (small, small))
            if os.path.exists(pp):
                self.poison_img = pygame.image.load(pp).convert_alpha()
                small = max(8, int(TILE * 0.4))
                self.poison_img_scaled = pygame.transform.smoothscale(self.poison_img, (small, small))
        except Exception:
            self.apple_img = None
            self.apple_img_scaled = None
            self.poison_img = None
            self.poison_img_scaled = None

    def _compute_history_cost(self) -> int:
        total = 0
        cur = self.problem.initial
        apples = set(self.problem.apples_initial)
        buff = 0
        poisons = set(self.problem.poisons_initial)
        poison_active = False
        for a in self.history:
            next_state = None
            for aa, ns, c in self.problem.successors(cur):
                if aa == a:
                    next_state = ns
                    break
            if next_state is None:
                step = 1
                if poison_active:
                    step += 3
                total += step
                continue
            pushed = cur.boxes != next_state.boxes
            if next_state.player in apples:
                apples.remove(next_state.player)
                buff = 10
            if next_state.player in poisons:
                poisons.remove(next_state.player)
                poison_active = True
            if pushed:
                dest = None
                for b in next_state.boxes:
                    if b not in cur.boxes:
                        dest = b
                        break
                if dest and dest in apples:
                    apples.remove(dest)
            base = 1
            if pushed:
                base = 1 if buff > 0 else 5
            step_cost = base + (3 if poison_active else 0)
            total += step_cost
            if buff > 0:
                buff -= 1
            cur = next_state
        return total

    def reset(self):
        self.problem = SokobanProblem(self.grid, use_deadlocks=self.problem.use_deadlocks)
        self.state = self.problem.initial
        self.history.clear()
        self.solver = None
        self.anim = None
        self.plan_autoplay = False
        self.level_complete = False
        self.completion_cost = None
        if hasattr(self, "_overlay_text"):
            delattr(self, "_overlay_text")
        self.apples = set(self.problem.apples_initial)
        self.apple_buff_steps = 0
        self.poisons = set(self.problem.poisons_initial)
        self.poison_active = False
        self.facing = "D"

    def cycle_level(self):
        self.level_idx = (self.level_idx + 1) % len(SAMPLE_LEVELS)
        self.grid = SAMPLE_LEVELS[self.level_idx]
        self.reset()

    def _apply_action_if_legal(self, a: str) -> Optional[State]:
        for aa, ns, _ in self.problem.successors(self.state):
            if aa == a:
                return ns
        return None

    def move(self, a: str):
        if self.anim:
            return
        ns = self._apply_action_if_legal(a)
        if ns is None:
            return
        self.anim = {
            "start": self.state,
            "end": ns,
            "a": a,
            "t": 0.0,
            "dur": 0.12,
        }
        self.facing = a

    def finish_anim(self):
        if not self.anim:
            return
        st: State = self.anim["start"]
        en: State = self.anim["end"]
        a = self.anim["a"]
        self.state = en
        self.history.append(a)
        if self.state.player in self.apples:
            self.apples.remove(self.state.player)
            self.apple_buff_steps = 10
        if self.state.player in self.poisons:
            self.poisons.remove(self.state.player)
            self.poison_active = True
        if st.boxes != en.boxes:
            moved_to = None
            for b in en.boxes:
                if b not in st.boxes:
                    moved_to = b
                    break
            if moved_to and moved_to in self.apples:
                self.apples.remove(moved_to)
        if self.apple_buff_steps > 0:
            self.apple_buff_steps -= 1
        self.anim = None
        if self.problem.is_goal(self.state):
            self.level_complete = True
            self.plan_autoplay = False
            self.completion_cost = self._compute_history_cost()
            if hasattr(self, "_overlay_text"):
                delattr(self, "_overlay_text")

    def compute_plan(self):
        algo = ALGO_NAMES[self.algo_idx]
        self.solver = Solver(self.problem)
        try:
            self.solver.compute(algo)
            self.plan_autoplay = True if self.solver.plan else False
        except NotImplementedError as e:
            self.solver = None
            self.plan_autoplay = False
            self._overlay_text = str(e)

    def step_plan(self):
        if not self.solver or not self.solver.plan or self.anim:
            return
        a = self.solver.plan.pop(0)
        self.move(a)
        if not self.solver.plan:
            self.plan_autoplay = False

    def _board_rect(self) -> pygame.Rect:
        return pygame.Rect(MARGIN, MARGIN, self.problem.w * TILE, self.problem.h * TILE)

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def _draw_panel(self, screen: pygame.Surface, rect: pygame.Rect, radius: int = 12):
        pygame.draw.rect(screen, COLORS["panel"], rect, border_radius=radius)
        pygame.draw.rect(screen, COLORS["panel_border"], rect, 1, border_radius=radius)

    def _draw_shadow(self, screen: pygame.Surface, rect: pygame.Rect):
        shadow = pygame.Surface((rect.w+8, rect.h+8), pygame.SRCALPHA)
        shadow.fill((0,0,0,0))
        pygame.draw.rect(shadow, (*COLORS["shadow"], 60), shadow.get_rect(), border_radius=14)
        screen.blit(shadow, (rect.x-4, rect.y-2))

    def _tile_to_px(self, x: int, y: int) -> Tuple[int,int]:
        br = self._board_rect()
        return br.x + x*TILE, br.y + y*TILE

    def _draw_grid(self, screen: pygame.Surface):
        br = self._board_rect()
        self._draw_shadow(screen, br)
        self._draw_panel(screen, br)
        for y in range(self.problem.h+1):
            ypx = br.y + y*TILE
            pygame.draw.line(screen, COLORS["grid"], (br.x, ypx), (br.right, ypx), 1)
        for x in range(self.problem.w+1):
            xpx = br.x + x*TILE
            pygame.draw.line(screen, COLORS["grid"], (xpx, br.y), (xpx, br.bottom), 1)

    def _draw_walls(self, screen: pygame.Surface):
        for (x, y) in self.problem.walls:
            px, py = self._tile_to_px(x, y)
            rect = pygame.Rect(px, py, TILE, TILE)
            pygame.draw.rect(screen, COLORS["wall"], rect, border_radius=6)

    def _draw_goals(self, screen: pygame.Surface):
        for (gx, gy) in self.problem.goals:
            px, py = self._tile_to_px(gx, gy)
            cx, cy = px + TILE//2, py + TILE//2
            gfx.aacircle(screen, cx, cy, TILE//7, COLORS["goal"])
            gfx.filled_circle(screen, cx, cy, TILE//7, COLORS["goal"])

    def _draw_apples(self, screen: pygame.Surface):
        for (ax, ay) in self.apples:
            px, py = self._tile_to_px(ax, ay)
            if self.apple_img_scaled is not None:
                iw, ih = self.apple_img_scaled.get_size()
                screen.blit(self.apple_img_scaled, (px + (TILE - iw)//2, py + (TILE - ih)//2))
            else:
                cx, cy = px + TILE//2, py + TILE//2
                r = max(6, TILE//5)
                gfx.aacircle(screen, cx, cy, r, COLORS["apple"])
                gfx.filled_circle(screen, cx, cy, r, COLORS["apple"])
                leaf_rect = pygame.Rect(cx + r//2, cy - r, r, r)
                pygame.draw.ellipse(screen, COLORS["apple_leaf"], leaf_rect)

    def _draw_poisons(self, screen: pygame.Surface):
        for (pxx, pyy) in self.poisons:
            px, py = self._tile_to_px(pxx, pyy)
            if self.poison_img_scaled is not None:
                iw, ih = self.poison_img_scaled.get_size()
                screen.blit(self.poison_img_scaled, (px + (TILE - iw)//2, py + (TILE - ih)//2))
            else:
                cx, cy = px + TILE//2, py + TILE//2
                r = max(5, TILE//6)
                gfx.aacircle(screen, cx, cy, r, COLORS["poison"])
                gfx.filled_circle(screen, cx, cy, r, COLORS["poison"])
                gfx.aacircle(screen, cx, cy, max(2, r//2), COLORS["poison_core"])
                gfx.filled_circle(screen, cx, cy, max(2, r//2), COLORS["poison_core"])

    def _draw_boxes_and_player(self, screen: pygame.Surface, dt: float):
        boxes = set(self.state.boxes)
        ppos = self.state.player
        if self.anim:
            st: State = self.anim["start"]
            en: State = self.anim["end"]
            a = self.anim["a"]
            t = min(self.anim["t"], self.anim["dur"]) / self.anim["dur"]
            dx, dy = DIRS[a]
            ppos = (st.player[0] + dx * t, st.player[1] + dy * t)
            moved_box = None
            for b in st.boxes:
                if b not in en.boxes:
                    moved_box = b
                    break
            if moved_box is not None:
                after = (moved_box[0] + dx * t, moved_box[1] + dy * t)
                boxes.remove(moved_box)
                boxes.add(after)

        for (bx, by) in boxes:
            px, py = self._tile_to_px(int(bx), int(by))
            fx = (bx - int(bx)) * TILE
            fy = (by - int(by)) * TILE
            rect = pygame.Rect(px + 6 + fx, py + 6 + fy, TILE - 12, TILE - 12)
            on_goal = (round(bx), round(by)) in self.problem.goals
            if self.box_img_scaled is not None:
                screen.blit(self.box_img_scaled, (rect.x, rect.y))
                if on_goal:
                    pygame.draw.rect(screen, COLORS["box_on_goal"], rect, width=3, border_radius=10)
            else:
                pygame.draw.rect(screen, COLORS["box_on_goal"] if on_goal else COLORS["box"], rect, border_radius=10)

        px, py = self._tile_to_px(int(ppos[0]), int(ppos[1]))
        fx = (ppos[0] - int(ppos[0])) * TILE
        fy = (ppos[1] - int(ppos[1])) * TILE
        if self.player_imgs_scaled and self.facing in self.player_imgs_scaled:
            img = self.player_imgs_scaled[self.facing]
            draw_x = int(px + 6 + fx)
            draw_y = int(py + 6 + fy)
            screen.blit(img, (draw_x, draw_y))
        else:
            cx, cy = int(px + TILE//2 + fx), int(py + TILE//2 + fy)
            gfx.aacircle(screen, cx, cy, TILE//3, COLORS["player"])
            gfx.filled_circle(screen, cx, cy, TILE//3, COLORS["player"])

    def draw(self, screen: pygame.Surface, dt: float):
        screen.fill(COLORS["bg"])
        self._draw_grid(screen)
        self._draw_walls(screen)
        self._draw_goals(screen)
        self._draw_apples(screen)
        self._draw_poisons(screen)
        self._draw_boxes_and_player(screen, dt)

    def draw_hud(self, screen: pygame.Surface):
        if self.font is None:
            self.font = pygame.font.Font(FONT_NAME, 18)
            self.info_font = pygame.font.Font(FONT_NAME, 16)
            self.overlay_font = pygame.font.Font(FONT_NAME, 28)
        br = self._board_rect()
        rect = pygame.Rect(MARGIN, br.bottom + 12, br.w, BANNER_H)
        self._draw_panel(screen, rect, radius=10)
        pygame.draw.line(screen, COLORS["panel_border"], (rect.x, rect.y), (rect.right, rect.y), 1)
        algo = ALGO_NAMES[self.algo_idx].upper()
        cost_val = self._compute_history_cost()
        time_str = "—"
        if self.solver and self.solver.stats:
            st = self.solver.stats
            if "time_ms" in st:
                try:
                    time_str = f"{int(st['time_ms'])} ms"
                except Exception:
                    time_str = f"{st['time_ms']} ms"
            elif "time_s" in st:
                try:
                    time_str = f"{int(float(st['time_s'])*1000)} ms"
                except Exception:
                    time_str = f"{st['time_s']} s"
        info1 = (
            f"Level {self.level_idx}  |  Algo: {algo}  |  Moves: {len(self.history)}  |  "
            f"Cost: {cost_val}  |  Time: {time_str}"
        )
        info2 = "Keys: Arrows=move  R=reset  Tab=algo  S=solve  N=step  L=next  Q/Esc=quit"
        surf1 = self.info_font.render(info1, True, COLORS["text"])
        surf2 = self.info_font.render(info2, True, COLORS["text"])
        screen.blit(surf1, (rect.x + 12, rect.y + 10))
        screen.blit(surf2, (rect.x + 12, rect.y + 36))
        if self.level_complete:
            br = self._board_rect()
            dim = pygame.Surface((br.w, br.h), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 240))
            screen.blit(dim, (br.x, br.y))
            t = ""
            if self.solver and self.solver.stats:
                st = self.solver.stats
                if "time_ms" in st:
                    try:
                        t = f"  Time: {int(st['time_ms'])} ms"
                    except Exception:
                        t = f"  Time: {st['time_ms']} ms"
                elif "time_s" in st:
                    try:
                        t = f"  Time: {int(float(st['time_s'])*1000)} ms"
                    except Exception:
                        t = f"  Time: {st['time_s']} s"
            msg = f"Level complete! Cost: {self.completion_cost}{t}"
            color = (30, 140, 60)
            font = getattr(self, "overlay_font", None) or self.font
            surf = font.render(msg, True, color)
            br = self._board_rect()
            x = br.x + (br.w - surf.get_width()) // 2
            y = br.y + (br.h - surf.get_height()) // 2 - 20
            screen.blit(surf, (x, y))
        elif self.solver and self.solver.stats:
            msg = self.solver.status_msg
            surf = self.font.render(msg, True, COLORS["text"])
            screen.blit(surf, (rect.x + 12, rect.y - 26))
        elif hasattr(self, "_overlay_text"):
            overlay_msg = str(getattr(self, "_overlay_text"))
            color = (140, 20, 20)
            font = getattr(self, "overlay_font", None) or self.font
            surf = font.render(overlay_msg, True, color)
            screen.blit(surf, (rect.x + 12, rect.y - 50))

def main():
    pygame.init()
    grid = SAMPLE_LEVELS[0]
    w = max(len(r) for r in grid)
    h = len(grid)
    screen_w = w*TILE + MARGIN*2
    screen_h = h*TILE + MARGIN*2 + BANNER_H + 12
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Sokoban AI")
    clock = pygame.time.Clock()
    game = Game(level_idx=0, use_deadlocks=True)

    running = True
    last_time = time.perf_counter()
    while running:
        now = time.perf_counter()
        dt = now - last_time
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_l:
                    game.cycle_level()
                    w = game.problem.w
                    h = game.problem.h
                    screen_w = w*TILE + MARGIN*2
                    screen_h = h*TILE + MARGIN*2 + BANNER_H + 12
                    screen = pygame.display.set_mode((screen_w, screen_h))
                elif game.level_complete:
                    pass
                elif event.key == pygame.K_TAB:
                    game.algo_idx = (game.algo_idx + 1) % len(ALGO_NAMES)
                elif event.key == pygame.K_s:
                    game.compute_plan()
                elif event.key == pygame.K_n:
                    game.step_plan()
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    keymap = {
                        pygame.K_UP: "U",
                        pygame.K_DOWN: "D",
                        pygame.K_LEFT: "L",
                        pygame.K_RIGHT: "R",
                    }
                    game.move(keymap[event.key])

        if game.anim:
            game.anim["t"] += dt
            if game.anim["t"] >= game.anim["dur"]:
                game.finish_anim()
        elif game.plan_autoplay and game.solver:
            game.step_plan()
        elif (not game.level_complete) and game.problem.is_goal(game.state):
            game.level_complete = True
            game.plan_autoplay = False
            game.completion_cost = game._compute_history_cost()
            if hasattr(game, "_overlay_text"):
                delattr(game, "_overlay_text")

        game.draw(screen, dt)
        game.draw_hud(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
        pygame.quit()
        sys.exit(1)