from sudokutools.coord import surrounding_coords
from sudokutools.solve import Bruteforce
from sudokutools.sudoku import ALL_INDICES


class SudokuAnalyzer(object):
    @classmethod
    def is_unique(cls, sudoku):
        """


        >>> from sudokutools.sudoku import Sudoku
        >>> from sudokutools.analyze import SudokuAnalyzer
        >>> sudoku1 = Sudoku.from_str("0505")
        >>> sudoku2 = Sudoku.from_str("123456789")
        >>> str(SudokuAnalyzer.is_unique(sudoku1))
        'None'
        >>> SudokuAnalyzer.is_unique(sudoku2)
        False
        """

        # Throw away conflicting sudokus
        if cls.find_all_conflicts(sudoku):
            return None

        sud1 = sudoku.copy()
        if not Bruteforce.call(sud1):
            return False

        sud2 = sudoku.copy()
        Bruteforce.call(sud2, reverse=True)

        if str(sud1) == str(sud2):
            return True
        else:
            return False

    @classmethod
    def find_conflicts(cls, sudoku, (x, y)):
        """Return a list of conflict tuples ((x, y), (i, j), value)
        """
        value = sudoku[x, y]
        if value == 0:
            return []

        coords = surrounding_coords((x, y), include=False)
        return [((x, y), (i, j), value) for (i, j) in coords if
                sudoku[i, j] == value]

    @classmethod
    def find_all_conflicts(cls, sudoku):
        conflicts = []
        for x in ALL_INDICES:
            for y in ALL_INDICES:
                xy_conflicts = cls.find_conflicts(sudoku, (x, y))
                conflicts.extend(xy_conflicts)

        return conflicts

    @classmethod
    def is_complete(cls, sudoku):
        return len(sudoku.empty) == 0 and not cls.find_all_conflicts(sudoku)