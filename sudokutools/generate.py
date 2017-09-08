
from sudokutools.analyze import SudokuAnalyzer
from sudokutools.solve import Bruteforce, CalculateCandidates
from sudokutools.sudoku import Sudoku, VALID_NUMBERS, ALL_INDICES

from random import choice, shuffle


class SudokuGenerator(object):
    @classmethod
    def create(cls, count=20):
        while True:
            sudoku = cls.seed(count=count)
            sol1 = sudoku.copy()
            if not Bruteforce.call(sol1):
                print("Found invalid sudoku - ignoring.")
                continue

            sol2 = sudoku.copy()
            Bruteforce.call(sol2, reverse=True)

            # sudoku is not unique - try to fix this.
            if sol1 != sol2:
                len1 = len(sudoku)
                cls.__fix_non_unique(sudoku, sol1, sol2)
                len2 = len(sudoku)
                print("Corrected non-unique sudoku: %d -> %d" % (len1, len2))

            else:
                len1 = len(sudoku)
                print("Found unique sudoku: %d" % len1)

            len1 = len(sudoku)
            cls.linear_minimize(sudoku)
            len2 = len(sudoku)
            print("Minimized sudoku: %d -> %d" % (len1, len2))

            return sudoku

    @classmethod
    def linear_minimize(cls, sudoku):
        for (x, y) in sudoku.filled:
            val = sudoku[(x, y)]
            sudoku[(x, y)] = 0
            if len(CalculateCandidates.call(sudoku, (x, y))) > 1:
                sudoku[(x, y)] = val

    @classmethod
    def __fix_non_unique(cls, sudoku, sol1, sol2):
        diffs = sol1.compare(sol2)
        shuffle(diffs)
        for (x, y), val1, val2 in diffs:
            sudoku[(x, y)] = val1

        return SudokuAnalyzer.is_unique(sudoku)

    @classmethod
    def seed(cls, count=20):
        """Return a sudoku with _at_most_ count filled fields.
        """
        sudoku = Sudoku()
        c = 0

        while c < count:
            x, y = choice(ALL_INDICES), choice(ALL_INDICES)
            if not sudoku[(x, y)]:
                sudoku[(x, y)] = choice(VALID_NUMBERS)
                if SudokuAnalyzer.find_conflicts(sudoku, (x, y)):
                    sudoku[(x, y)] = 0
                c += 1

        return sudoku
