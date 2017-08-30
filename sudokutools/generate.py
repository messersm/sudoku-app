
from sudokutools.analyze import SudokuAnalyzer
from sudokutools.solve import Bruteforce
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
            if sol1 == sol2:
                print("Found unique sudoku - returning.")
                return sudoku
            # sudoku is not unique - try to fix this.
            else:
                print("Found non-unique sudoku - correcting.")
                return cls.__fix_non_unique(sudoku, sol1, sol2)

    @classmethod
    def __fix_non_unique(cls, sudoku, sol1, sol2):
        diffs = sol1.compare(sol2)
        shuffle(diffs)
        for (x, y), val1, val2 in diffs:
            sudoku[(x, y)] = val1
            sol2 = sudoku.copy()
            Bruteforce.call(sol2, reverse=True)
            if sol1 == sol2:
                return sudoku

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
