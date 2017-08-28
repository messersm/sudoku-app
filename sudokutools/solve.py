# standard imports
from collections import namedtuple

# local imports
from sudokutools.coord import column_coords, row_coords, \
    quad_coords, surrounding_coords

# constants
VALID_NUMBERS = (1, 2, 3, 4, 5, 6, 7, 8, 9)

# Results #
BaseResult = namedtuple("BaseResult", ["method", "sudoku", "coords", "value"])


class NumberResult(BaseResult):
    def apply(self, sudoku=None):
        if not sudoku:
            sudoku = self.sudoku
        sudoku[self.coords] = self.value


class CandidatesResult(BaseResult):
    def apply(self, sudoku=None):
        if not sudoku:
            sudoku = self.sudoku
        sudoku.candidates[self.coords] = self.value


# Solve methods #
class SolveMethod(object):
    priority = 0

    @classmethod
    def search(cls, sudoku):
        for (x, y) in sudoku.empty:
            result = cls.search_field(sudoku, (x, y))
            if result:
                yield result

    @classmethod
    def search_field(cls, sudoku, (x, y)):
        raise NotImplementedError("Implement in subclass!")

    @classmethod
    def apply(cls, sudoku, inplace=True):
        if not inplace:
            sudoku = sudoku.copy()
        for result in cls.search(sudoku):
            result.apply()
        return sudoku

    @classmethod
    def apply_field(cls, sudoku, (x, y), inplace=True):
        result = cls.search_field(sudoku, (x, y))
        if result:
            if not inplace:
                sudoku = sudoku.copy()
            result.apply(sudoku)
        return sudoku


class CalculateCandidates(SolveMethod):
    priority = 0

    @classmethod
    def search(cls, sudoku):
        for x in range(9):
            for y in range(9):
                result = cls.search_field(sudoku, (x, y))
                if result:
                    yield result

    @classmethod
    def search_field(cls, sudoku, (x, y)):
        return CandidatesResult(
            cls, sudoku, (x, y), cls.call(sudoku, (x, y)))

    @classmethod
    def call(cls, sudoku, (x, y)):
        """

        Example:
        >>> from sudokutools.sudoku2 import Sudoku
        >>> sud = Sudoku.from_str("123456709")
        >>> CalculateCandidates.call(sud, (7, 0))
        [8]
        """
        candidates = list(VALID_NUMBERS)

        for (i, j) in surrounding_coords((x, y), include=False):
            if sudoku[(i, j)] in candidates:
                candidates.remove(sudoku[(i, j)])

        return candidates


class NakedSingle(SolveMethod):
    priority = 5

    @classmethod
    def search_field(cls, sudoku, (x, y)):
        candidates = sudoku.candidates[(x, y)]
        if len(candidates) == 1:
            return NumberResult(cls, sudoku, (x, y), candidates[0])


class HiddenSingle(SolveMethod):
    priority = 5

    @classmethod
    def search_field(cls, sudoku, (x, y)):
        for f in column_coords, row_coords, quad_coords:
            other_candidates = []
            for (i, j) in f((x, y), include=False):
                other_candidates.extend(sudoku.candidates[(i, j)])

            for number in VALID_NUMBERS:
                if number not in other_candidates:
                    return NumberResult(cls, sudoku, (x, y), number)


class Bruteforce(SolveMethod):
    priority = 20

    @classmethod
    def call(cls, sudoku, reverse=False):
        if not sudoku.empty:
            return sudoku

        # apply changes to a new sudoku
        new_sudoku = sudoku.copy()
        CalculateCandidates.apply(new_sudoku)

        sorted_empty = sorted(
            sudoku.empty,
            key=lambda (x, y): len(new_sudoku.candidates[(x, y)]))

        next_coord = sorted_empty[0]
        next_candidates = new_sudoku.candidates[next_coord]

        if reverse:
            next_candidates = reversed(next_candidates)
        for candidate in next_candidates:
            new_sudoku[next_coord] = candidate

            solved_sudoku = cls.call(new_sudoku, reverse=reverse)
            if solved_sudoku:
                return solved_sudoku
            # else continue

        # If we do reach this point, no candidate was valid, thus
        # the sudoku is not solveable.
        return None

    @classmethod
    def search(cls, sudoku):
        new_sudoku = cls.call(sudoku)
        for (x, y) in sudoku.empty:
            if new_sudoku[(x, y)]:
                yield NumberResult(cls, sudoku, (x, y), new_sudoku[(x, y)])

    @classmethod
    def search_field(cls, sudoku, (x, y)):
        for result in Bruteforce.search(sudoku):
            if result.coords == (x, y):
                return result

# all solve methods
SOLVE_METHODS = [
    NakedSingle,
    HiddenSingle,
    Bruteforce
]


# Solver #
class SudokuSolver(object):
    def __init__(self, methods=None):
        if methods is None:
            self.methods = list(SOLVE_METHODS)
        else:
            self.methods = list(methods)

        self.methods.sort(key=lambda m: m.priority)

    def solve(self, sudoku, inplace=True):
        """Solves the sudoku (in place!)
        """

        if not inplace:
            sudoku = sudoku.copy()

        while True:
            empty_count = len(sudoku.empty)
            if empty_count == 0:
                break

            # Recalculate candidates in each round
            CalculateCandidates.apply(sudoku)
            for m in self.methods:
                m.apply(sudoku)

            # Couldn't solve
            if len(sudoku.empty) == empty_count:
                break

        return sudoku

    def __str__(self):
        return ''

class SudokuAnalyzer(object):
    @classmethod
    def is_unique(cls, sudoku):
        sud1 = Bruteforce.call(sudoku)
        if not sud1:
            return None
        sud2 = Bruteforce.call(sudoku, reverse=True)

        if sud1 == sud2:
            return True
        else:
            return False


def solve(sudoku, *args, **kwargs):
    """
    >>> from sudokutools.examples import EXAMPLES
    >>> from sudokutools.solve import solve
    >>> from sudokutools.sudoku2 import Sudoku
    >>> solve_works = True
    >>> for example, solution in EXAMPLES:
    ...     sudoku = Sudoku.from_str(example)
    ...     solved = solve(sudoku)
    ...     solve_works &= (str(solved) == solution.strip())
    >>> solve_works
    True
    """
    return SudokuSolver(*args, **kwargs).solve(sudoku)


if __name__ == '__main__':
    import doctest
    doctest.testmod()