from crossword import *
from creator import *
import sys
import time


def display_solution(crossword, assignment):
    """Prints the crossword with solved words on CLI."""
    grid = [['#' if not crossword.struct[i][j] else '_' for j in range(crossword.width)]
            for i in range(crossword.height)]

    for var, word in assignment.items():
        for k, (i, j) in enumerate(var.cells):
            grid[i][j] = word[k]

    print("\n🧩 Solved Crossword:\n")
    for row in grid:
        print(' '.join(row))
    print("\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <puzzle_file>")
        print("Example: python main.py puzzles/p1.txt")
        sys.exit(1)

    puzzle_file = sys.argv[1]

    crossword = Crossword(puzzle_file, 'words/words.txt')
    creator = Creator(crossword, heuristic=True)

    start = time.perf_counter()
    assignment = creator.solve()
    runtime = time.perf_counter() - start

    if assignment:
        print(f"✅ Crossword solved in {runtime:.2f} seconds!")
        display_solution(crossword, assignment)
    else:
        print("❌ No solution found.")


if __name__ == "__main__":
    main()
