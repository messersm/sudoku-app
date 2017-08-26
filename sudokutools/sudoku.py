from functools import wraps
from copy import deepcopy

from examples import EXAMPLES
from coord import column_coords, row_coords, \
    quad_coords, surrounding_coords

VALID_NUMBERS = (1, 2, 3, 4, 5, 6, 7, 8, 9)
ALL_NUMBERS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
ALL_INDECES = (0, 1, 2, 3, 4, 5, 6, 7, 8)

class Sudoku(object):
    def __init__(self, numbers=None):
        if numbers:
            self.numbers = numbers
        else:
            self.numbers = []
            for i in ALL_INDECES:
                self.numbers.append([0 for j in ALL_INDECES])
    
    def __setitem__(self, (x, y), value):
        """Set Sudoku to value at (x, y)

        Examples:
        >>> s = [str(i) for i in range(1, 10)]
        >>> s *= 9
        >>> sud = Sudoku.from_str(s)
        >>> sud[4, 2] = 9
        >>> sud[1, 1] = 0
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

        # YES: it's (y, x)
        self.numbers[y][x] = value

    def __getitem__(self, (x, y)):
        """

        Examples:
        >>> sud = Sudoku()
        >>> sud['0', 1] # doctest:+ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        >>> sud[0, 11] # doctest:+ELLIPSIS
        Traceback (most recent call last):
            ...
        IndexError: ...
        >>> sud[3, 4]
        0
        >>> sud[3, 4] = 5
        >>> sud[3, 4]
        5
        """
        return self.numbers[y][x]

    def __get_values(self, *coords):
        return [self[x, y] for (x, y) in coords]

    def column(self, (x, y)):
        """
        >>> sud = Sudoku.from_str("123456789.777", ignore=('.'))
        >>> sud.column((1, 5))
        [2, 7, 0, 0, 0, 0, 0, 0, 0]
        """
        return [row[x] for row in self.numbers]

    def row(self, (x, y)):
        return list(self.numbers[y])

    def grid(self, (x, y)):
        """
        >>> sud = Sudoku.from_str("123456789.777", ignore=('.'))
        >>> sud.grid((1, 2))
        [1, 2, 3, 7, 7, 7, 0, 0, 0]
        """
        x -= x % 3
        y -= y % 3

        g = []
        for row in self.numbers[y:y+3]:
            g.extend(row[x:x+3])

        return g

    def find_conflicts(self, (x, y)):
        """Return a list of conflict tuples ((x, y), (i, j), value)
        """
        value = self[x, y]
        if value == 0:
            return []
        
        coords = surrounding_coords((x, y), include=False)
        return [((x, y), (i, j), value) for (i, j) in coords if self[i, j] == value]

    def find_all_conflicts(self):
        conflicts = []
        for x in ALL_INDECES:
            for y in ALL_INDECES:
                xy_conflicts = self.find_conflicts((x, y))
                conflicts.extend(xy_conflicts)
                
        return conflicts

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
        for y in ALL_INDECES:
            column = []

            for x in ALL_INDECES:
                if self[x, y] == 0:
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
                sud[x, y] = 0
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
        return [(x, y) for x in ALL_INDECES for y in ALL_INDECES if self[x, y] == 0]

    def candidates(self, (x, y)):
        """Return a set of numbers that can be at (x, y).

        Example:
        >>> sud = Sudoku.from_str("087054301")
        >>> sud.candidates((0, 0))
        [2, 6, 9]
        >>> sud.candidates((1, 0))
        [8]
        """

        if self[x, y]:
            return [self[x, y]]

        candidates = set(VALID_NUMBERS)
        candidates -= set(self.grid((x, y)))
        candidates -= set(self.column((x, y)))
        candidates -= set(self.row((x, y)))

        return list(candidates)

    def indirect_candidates(self, (x, y), *coords):
        """
        """
        candidates = list(VALID_NUMBERS)
        coords = list(coords)
        try:
            coords.remove((x, y))
        except:
            pass

        others = []
        for coord in coords:
            others.extend(self.candidates(coord))

        return [num for num in VALID_NUMBERS if num not in others]

    def bruteforce(self, candidates=None):
        """Returns a completly solved Sudoku instance or None

        >>> sudoku = Sudoku.from_str(EXAMPLES[1][0])
        >>> solved = sudoku.bruteforce()
        >>> str(sudoku) == EXAMPLES[1][0].strip()
        True
        >>> str(solved) == EXAMPLES[1][1].strip()
        True
        """

        # check this sudoku for being complete
        empty = self.empty_coords()
        
        if not empty:
            return self

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

    def naked_single(self, (x, y)):
        cand = self.candidates((x, y))
        if len(cand) == 1:
            return ((x, y), cand.pop(), "naked single")
        else:
            return None

    def hidden_single(self, (x, y)):
        for f in column_coords, row_coords, quad_coords:
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

        >>> solve_works = True
        >>> for example, solution in EXAMPLES:
        ...     sud = Sudoku.from_str(example)
        ...     sud.solve()
        ...     solve_works &= (str(sud) == solution.strip())
        >>> solve_works
        True
        """

        if self.find_all_conflicts():
            return
        else:
            self.apply_steps(self.iter_steps())

    def solve_field(self, (x, y)):
        sudoku = self.copy()
        for ((i, j), value, step_type) in sudoku.iter_steps():
            if (x, y) == (i, j):
                self[x, y] = value
                break

    def copy(self):
        return Sudoku(numbers=deepcopy(self.numbers))

class SudokuWithCandidates(Sudoku):
    def __init__(self, numbers=None, candidates=None):
        super(SudokuWithCandidates, self).__init__(numbers=numbers)
        if candidates:
            self.__candidates = candidates
        else:
            self.__candidates = {}

    def set_candidates(self, (x, y), candidates):
        if candidates is None:
            self.__candidates.pop((x, y), None)
        else:
            for item in candidates:
                if item not in VALID_NUMBERS:
                    raise ValueError("Candidates must be between 1 and 9.")
            self.__candidates[(x, y)] = list(candidates)

    def get_candidates(self, (x, y)):
        return self.__candidates.get((x, y), None)

    def copy(self):
        return SudokuWithCandidates(
            numbers=deepcopy(self.numbers),
            candidates=deepcopy(self.__candidates))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
