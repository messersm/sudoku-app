# standard imports
from collections import namedtuple

# local imports
from sudokutools.coord import column_coords, row_coords, \
    quad_coords, surrounding_coords

# constants
VALID_NUMBERS = (1, 2, 3, 4, 5, 6, 7, 8, 9)

# Results #
BaseResult = namedtuple("BaseResult", ["method", "sudoku", "coords", "value"])


class SetNumber(BaseResult):
    def apply(self, sudoku=None):
        if not sudoku:
            sudoku = self.sudoku
        sudoku[self.coords] = self.value


class SetCandidates(BaseResult):
    def apply(self, sudoku=None):
        if not sudoku:
            sudoku = self.sudoku
        sudoku.candidates[self.coords] = self.value


class RemoveCandidates(BaseResult):
    def apply(self, sudoku=None):
        if not sudoku:
            sudoku = self.sudoku
        for item in self.value:
            try:
                sudoku.candidates[self.coords].remove(item)
            except (KeyError, ValueError):
                pass


# Solve methods #
class SolveMethod(object):
    priority = 0

    @classmethod
    def search(cls, sudoku):
        for (x, y) in sudoku.empty:
            for result in cls.search_field(sudoku, (x, y)):
                yield result

    @classmethod
    def search_field(cls, sudoku, (x, y)):
        raise NotImplementedError("Implement in subclass!")

    @classmethod
    def apply(cls, sudoku):
        count = 0
        for result in cls.search(sudoku):
            result.apply()
            count += 1
        return count

    @classmethod
    def apply_field(cls, sudoku, (x, y)):
        count = 0
        for result in cls.search_field(sudoku, (x, y)):
            result.apply(sudoku)
            count +=1
        return count


class CalculateCandidates(SolveMethod):
    priority = 0

    @classmethod
    def search(cls, sudoku):
        for x in range(9):
            for y in range(9):
                for result in cls.search_field(sudoku, (x, y)):
                    yield result

    @classmethod
    def search_field(cls, sudoku, (x, y)):
        yield SetCandidates(
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
            value = candidates[0]
            yield SetNumber(cls, sudoku, (x, y), value)
            for (i, j) in surrounding_coords((x, y), include=False):
                yield RemoveCandidates(cls, sudoku, (i, j), [value])


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
                    for result in cls.__results(sudoku, (x, y), number):
                        yield result
                    raise StopIteration

    @classmethod
    def __results(cls, sudoku, (x, y), number):
        yield SetNumber(cls, sudoku, (x, y), number)
        for (i, j) in surrounding_coords((x, y), include=False):
            yield RemoveCandidates(cls, sudoku, (i, j), [number])


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
                yield SetNumber(cls, sudoku, (x, y), new_sudoku[(x, y)])

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

        # Calculate candidates first
        CalculateCandidates.apply(sudoku)

        while True:
            if not self._apply_methods(sudoku):
                break

        return sudoku

    def _apply_methods(self, sudoku):
        # apply all results of the first
        # method, that has results - then return
        count = 0
        for m in self.methods:
            count += m.apply(sudoku)
            if count > 0:
                return count
        return 0

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