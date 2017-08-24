from functools import wraps

EASY_EXAMPLE = """
003020600
900305001
001806400
008102900
700000008
006708200
002609500
800203009
005010300
"""

EASY_SOLUTION = """
483921657
967345821
251876493
548132976
729564138
136798245
372689514
814253769
695417382
"""

HARD_EXAMPLE = """
009003008
010040020
200700400
800600700
090070010
003004002
005001007
030090050
700400200
"""

HARD_SOLUTION = """
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

VALID_NUMBERS = (1, 2, 3, 4, 5, 6, 7, 8, 9)

def check_coords(f):
    """Decorator that checks, if the provided coordinates are valid."""
    @wraps(f)
    def wrapper(self, (x, y), *args, **kwargs):
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("x, y coordinates must be integers.")
        if x not in range(9) or y not in range(9):
            raise ValueError("x, y coordinates must be between 0 and 8.")

        return f(self, (x, y), *args, **kwargs)
    return wrapper

def require_empty(f):
    """Decorator that checks, if the provided field is empty."""
    @wraps(f)
    def wrapper(self, (x, y), *args, **kwargs):
        if self[x, y] is not None:
            raise ValueError("(%d, %d) is not an empty field.")
        return f(self, (x, y), *args, **kwargs)
    return wrapper

class Sudoku(dict):
    @check_coords
    def __setitem__(self, (x, y), value):
        """Set Sudoku to value at (x, y)

        Examples:
        >>> s = [str(i) for i in range(1, 10)]
        >>> s *= 9
        >>> sud = Sudoku.from_str(s)
        >>> sud[4, 2] = 9
        >>> sud[1, 1] = None
        >>> print(sud)
        123456789
        103456789
        123496789
        123456789
        123456789
        123456789
        123456789
        123456789
        123456789
        """

        if value is not None and value not in range(1, 10):
            raise ValueError("value must be between 1 and 9.")

        super(Sudoku, self).__setitem__((x, y), value)

    @check_coords
    def __getitem__(self, (x, y)):
        """

        Examples:
        >>> sud = Sudoku()
        >>> sud['0', 1]
        Traceback (most recent call last):
            ...
        TypeError: x, y coordinates must be integers.
        >>> sud[0, 11]
        Traceback (most recent call last):
            ...
        ValueError: x, y coordinates must be between 0 and 8.
        >>> str(sud[3, 4])
        'None'
        >>> sud[3, 4] = 5
        >>> sud[3, 4]
        5
        """
        return super(Sudoku, self).get((x, y), None)

    def __get_values(self, *coords):
        return [self[x, y] for (x, y) in coords]

    @check_coords
    def column_coords(self, (x, y)):
        return [(x, j) for j in range(9)]

    @check_coords
    def column(self, (x, y)):
        return self.__get_values(*self.column_coords((x, y)))

    @check_coords
    def row_coords(self, (x, y)):
        return [(i, y) for i in range(9)]

    @check_coords
    def row(self, (x, y)):
        return self.__get_values(*self.row_coords((x, y)))

    @check_coords
    def grid(self, (x, y)):
        return self.__get_values(*self.grid_coords((x, y)))

    @check_coords
    def grid_coords(self, (x, y)):
        """

        Examples:
        >>> sud = Sudoku()
        >>> sud.grid_coords((1, 1))
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        >>> sud.grid_coords((4, 8))
        [(3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)]
        """
        x -= x % 3
        y -= y % 3

        return [(x+i, y+j) for i in range(3) for j in range(3)]

    @check_coords
    def find_conflicts(self, (x, y)):
        """Return a list of conflict tuples ((x, y), (i, j), value)
        """
        value = self[x, y]
        if value is None:
            return []

        coords = self.column_coords((x, y))
        coords.extend(self.row_coords((x, y)))
        coords.extend(self.grid_coords((x, y)))
        while (x, y) in coords:
            coords.remove((x, y))

        return [((x, y), (i, j), value) for (i, j) in coords if self[i, j] == value]

    def find_all_conflicts(self):
        conflicts = []
        for x in range(9):
            for y in range(9):
                xy_conflicts = self.find_conflicts((x, y))


    def __str__(self):
        return self.to_str()

    def to_str(self, column_sep='', row_sep='\n', empty='0'):
        """

        Example:
        >>> s = [str(i) for i in range(1, 10)]
        >>> s *= 9
        >>> sud = Sudoku.from_str(s)
        >>> print(sud.to_str(column_sep='.'))
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        1.2.3.4.5.6.7.8.9
        """
        rows = []
        for y in range(9):
            column = []

            for x in range(9):
                if self[x, y] is None:
                    column.append(empty)
                else:
                    column.append(str(self[x, y]))

            rows.append(column_sep.join(column))
        return row_sep.join(rows)

    @classmethod
    def from_str(cls, s, empty=(' ', '0'), ignore=('\n', '\t')):
        """

        >>> s = [str(i) for i in range(1, 10)]
        >>> s *= 9
        >>> sud = Sudoku.from_str(s)
        >>> print(sud)
        123456789
        123456789
        123456789
        123456789
        123456789
        123456789
        123456789
        123456789
        123456789
        """
        x = 0
        y = 0

        sud = cls()

        for item in s:
            if item in ignore:
                continue
            elif item in empty:
                sud[x, y] = None
            else:
                sud[x, y] = int(item)
            x += 1
            if x >= 9:
                y += 1
                x = 0
            if y >= 9:
                break

        return sud

    def empty_coords(self):
        return [(x, y) for x in range(9) for y in range(9) if self[x, y] is None]

    def candidates(self, *coords):
        """Return a set of numbers that can be at (x, y).

        Example:
        >>> sud = Sudoku.from_str("087054301")
        >>> sud.candidates((0, 0))
        set([9, 2, 6])
        >>> sud.candidates((1, 0))
        set([8])
        >>> sud.candidates((0, 0), (1, 0))
        set([8, 9, 2, 6])

        >>> sud = Sudoku.from_str(HARD_EXAMPLE)
        >>> sud.candidates((0,0))
        set([4, 5, 6])
        >>> sud.candidates((1, 0))
        set([4, 5, 6, 7])
        >>> sud.candidates((0, 1))
        set([3, 5, 6])
        >>> coords = sud.grid_coords((0, 1))
        >>> coords.remove((0, 1))
        >>> sud.candidates(*coords)
        set([1, 2, 4, 5, 6, 7, 8, 9])
        """

        candidates = set()

        for (x, y) in coords:
            if self[x, y] is not None:
                cand = {self[x, y]}
            else:
                cand = set(range(1, 10))
                cand -= set(self.column((x, y)))
                cand -= set(self.row((x, y)))
                cand -= set(self.grid((x, y)))

            candidates |= cand

        return candidates

    def indirect_candidates(self, (x, y), *coords):
        """
        Example:
        >>> sud = Sudoku.from_str(HARD_EXAMPLE)
        >>> sud.indirect_candidates((0, 1), *sud.grid_coords((0, 1)))
        set([3])
        """
        candidates = set(range(1, 10))
        coords = list(coords)
        try:
            coords.remove((x, y))
        except:
            pass
        candidates -= self.candidates(*coords)
        return candidates

    def bruteforce(self):
        """Returns a completly solved Sudoku instance or None

        >>> sudoku = Sudoku.from_str(HARD_EXAMPLE)
        >>> solved = sudoku.bruteforce()
        >>> str(sudoku) == HARD_EXAMPLE.strip()
        True
        >>> str(solved) == HARD_SOLUTION.strip()
        True
        """

        # check this sudoku for being complete
        empty = self.empty_coords()
        conflicts = self.find_all_conflicts()
        
        if not empty and not conflicts:
            return self
        elif conflicts:
            return None

        # sort empty fields by candidate length and begin with the shortest (for performance)
        empty_and_candidates = [(coord, self.candidates(coord)) for coord in empty]
        empty_and_candidates.sort(key=lambda (coord, candidates): len(candidates))
        next_coord, next_candidates = empty_and_candidates[0]

        # apply changes to a new sudoku
        sudoku = self.copy()
        for candidate in next_candidates:
            sudoku[next_coord] = candidate
            solved_sudoku = sudoku.bruteforce()

            if solved_sudoku is not None:
                return solved_sudoku

        # If we do reach this point, no candidate was valid, thus
        # the sudoku is not solveable.
        return None

    def bruteforce_steps(self):
        steps = []
        
        solved = self.bruteforce()
        if solved is None:
            return steps
        
        for (x, y) in self.empty_coords():
            steps.append(((x, y), solved[x, y], "bruteforce"))

        return steps

    @require_empty
    @check_coords
    def naked_single(self, (x, y)):
        cand = self.candidates((x, y))
        if len(cand) == 1:
            return ((x, y), cand.pop(), "naked single")
        else:
            return None

    @require_empty
    @check_coords
    def hidden_single(self, (x, y)):
        for f in self.column_coords, self.row_coords, \
                 self.grid_coords:

            cand = self.indirect_candidates((x, y), *f((x, y)))
            if len(cand) == 1:
                return ((x, y), cand.pop(), "hidden single")
        return None

    def apply_steps(self, steps, check_conflicts=False):
        for ((x, y), value, step_type) in steps:
            oldval = self[x, y]
            self[x, y] = value

            if check_conflicts and self.find_conflicts((x, y)):
                self[x, y] = oldval
                return

    def iter_steps(self):
        """iterate through all possible solve steps ((x, y), value, type).
        """

        steps = []
        empty = self.empty_coords()
        for coord in empty:
            value = self.naked_single(coord)
            if value:
                steps.append(value)
                yield value
                continue
            value = self.hidden_single(coord)
            if value:
                steps.append(value)
                yield value

        # solve the rest using bruteforce
        if len(steps) < len(empty):
            sud = self.copy()
            sud.apply_steps(steps)

            for step in sud.bruteforce_steps():
                yield step

    def step(self):
        for ((x, y), value, step_type) in self.iter_steps():
            self[x, y] = value
            return ((x, y), value, step_type)

    def solve(self):
        """Solve the Sudoku filling all (possible) fields.

        >>> sud = Sudoku.from_str(EASY_EXAMPLE)
        >>> sud.solve()
        >>> str(sud) == EASY_SOLUTION.strip()
        True
        >>> sud = Sudoku.from_str(HARD_EXAMPLE)
        >>> sud.solve()
        >>> str(sud) == HARD_SOLUTION.strip()
        True
        """
        self.apply_steps(self.iter_steps(), check_conflicts=True)

    def copy(self):
        sud = Sudoku()
        sud.update(self)
        return sud

class SudokuWithCandidates(Sudoku):
    def __init__(self):
        self.__candidates = {}

    @check_coords
    def set_candidates(self, (x, y), *candidates):
        for item in candidates:
            if item not in VALID_NUMBERS:
                raise ValueError("Candidates must be between 1 and 9.")
        self.__candidates[(x, y)] = candidates

    @check_coords
    def get_candidates(self, (x, y)):
        return self.__candidates.get((x, y), list())

    def copy(self):
        sud = SudokuWithCandidates()
        sud.update(self)
        for (x, y), candidates in self.__candidates.items():
            sud.set_candidates((x, y), *candidates)
        return sud

if __name__ == '__main__':
    import doctest
    doctest.testmod()
