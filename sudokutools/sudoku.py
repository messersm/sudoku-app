from copy import deepcopy

ALL_INDICES = (0, 1, 2, 3, 4, 5, 6, 7, 8)
VALID_NUMBERS = (1, 2, 3, 4, 5, 6, 7, 8, 9)


class Sudoku(object):
    def __init__(self, numbers=None, candidates=None):
        if numbers is None:
            self.numbers = []
            for i in ALL_INDICES:
                self.numbers.append([0 for j in ALL_INDICES])
        else:
            self.numbers = numbers

        if candidates is None:
            self.candidates = {}
        else:
            self.candidates = candidates

    def __setitem__(self, (x, y), value):
        self.numbers[y][x] = value

    def __getitem__(self, (x, y)):
        return self.numbers[y][x]

    @property
    def empty(self):
        return [(x, y) for x in ALL_INDICES for y in ALL_INDICES if not self[x, y]]

    def load_str(self, s, empty=('.', '0'), ignore=(' ', '\n', '\t')):
        """

        >>> s = [str(i) for i in range(1, 10)]
        >>> s *= 9
        >>> sud = Sudoku()
        >>> sud.load_str(s)
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

        for item in s:
            if item in ignore:
                continue
            elif item in empty:
                self[x, y] = 0
            else:
                self[x, y] = int(item)
            x += 1
            if x >= 9:
                y += 1
                x = 0
            if y >= 9:
                break

    @classmethod
    def from_str(cls, *args, **kwargs):
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

        >>> sudoku = Sudoku.from_str("0505")
        >>> print(sudoku)
        050500000
        000000000
        000000000
        000000000
        000000000
        000000000
        000000000
        000000000
        000000000
        """
        sud = cls()
        sud.load_str(*args, **kwargs)
        return sud

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
        for y in ALL_INDICES:
            column = []

            for x in ALL_INDICES:
                if self[x, y] == 0:
                    column.append(empty)
                else:
                    column.append(str(self[x, y]))

            rows.append(column_sep.join(column))
        return row_sep.join(rows)

    def copy(self):
        return Sudoku(
            numbers=deepcopy(self.numbers),
            candidates=deepcopy(self.candidates))