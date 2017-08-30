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

        Examples:
        >>> from sudokutools.sudoku import Sudoku
        >>> sudoku = Sudoku.from_str("123456709")
        >>> CalculateCandidates.call(sudoku, (7, 0))
        [8]
        >>> CalculateCandidates.call(sudoku, (0, 0))
        [1]
        """

        if sudoku[(x, y)]:
            return [sudoku[(x, y)]]

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
        """Solve sudoku _inplace_ returning success status

        Example:
        >>> from sudokutools.sudoku import Sudoku
        >>> from sudokutools.solve import Bruteforce
        >>> sudoku = Sudoku.from_str( \
            "009003008" + \
            "010040020" + \
            "200700400" + \
            "800600700" + \
            "090070010" + \
            "003004002" + \
            "005001007" + \
            "030090050" + \
            "700400200")
        >>> solution = Bruteforce.call(sudoku)
        >>> print(solution)
        469523178
        317948526
        258716439
        821659743
        694372815
        573184962
        945261387
        132897654
        786435291
        """

        empty = sudoku.empty
        if not empty:
            return True

        # (Re)calculate candidates
        CalculateCandidates.apply(sudoku)

        sorted_empty = sorted(
            empty,
            key=lambda (x, y): len(sudoku.candidates[(x, y)]))

        next_coord = sorted_empty[0]
        next_candidates = sudoku.candidates[next_coord]

        if reverse:
            next_candidates = reversed(next_candidates)
        for candidate in next_candidates:
            sudoku[next_coord] = candidate

            if cls.call(sudoku, reverse=reverse):
                return sudoku
            # else: continue with next candidate

        # If we do reach this point, no candidate was valid, thus
        # the sudoku is not solveable.
        # Revert changes (we work _inplace_)
        sudoku[next_coord] = 0
        return False

    @classmethod
    def search(cls, sudoku):
        new_sudoku = sudoku.copy()
        if not cls.call(sudoku):
            raise StopIteration
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

    def solve_field(self, sudoku, (x, y), inplace=True):
        if not inplace:
            sudoku = sudoku.copy()

        for m in self.methods:
            result = m.search_field(sudoku, (x, y))
            if result:
                result.apply()
                return sudoku

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


def solve(sudoku, inplace=True, **kwargs):
    """
    >>> from sudokutools.examples import EXAMPLES
    >>> from sudokutools.solve import solve
    >>> from sudokutools.sudoku import Sudoku
    >>> solve_works = True
    >>> for example, solution in EXAMPLES:
    ...     sudoku = Sudoku.from_str(example)
    ...     solved = solve(sudoku)
    ...     solve_works &= (str(solved) == solution.strip())
    >>> solve_works
    True
    """
    return SudokuSolver(**kwargs).solve(sudoku, inplace=inplace)


if __name__ == '__main__':
    import doctest
    doctest.testmod()