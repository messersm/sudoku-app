"""

"""

_ALL_INDECES = (0, 1, 2, 3, 4, 5, 6, 7, 8)

def column_coords((x, y), include=True):
    """
    Examples:
    >>> column_coords((2, 2))
    [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8)]
    >>> column_coords((2, 2), include=False)
    [(2, 0), (2, 1), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8)]
    """
    return [(x, j) for j in _ALL_INDECES if include or j != y]

def row_coords((x, y), include=True):
    """
    Examples:
    >>> row_coords((2, 2))
    [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2)]
    >>> row_coords((2, 2), include=False)
    [(0, 2), (1, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2)]
    """

    return [(i, y) for i in _ALL_INDECES if include or i != x]

def quad_coords((x, y), include=True):
    """

    Examples:
    >>> quad_coords((1, 1))
    [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
    >>> quad_coords((4, 8), include=False)
    [(3, 6), (4, 6), (5, 6), (3, 7), (4, 7), (5, 7), (3, 8), (5, 8)]
    """
    grid_x = x - (x % 3)
    grid_y = y - (y % 3)

    coords = [(grid_x+i, grid_y+j) for j in range(3) for i in range(3)]
    if not include:
        coords.remove((x, y))
    return coords

def surrounding_coords((x, y), include=True):
    """

    Tests:
    >>> coord = (3, 4)
    >>> c = set(column_coords(coord))
    >>> r = set(row_coords(coord))
    >>> q = set(quad_coords(coord))
    >>> s = set(surrounding_coords(coord))
    >>> s2 = set(surrounding_coords(coord, include=False))
    >>> len(s)
    21
    >>> s & c == c
    True
    >>> s & r == r
    True
    >>> s & q == q
    True
    >>> len(s2)
    20
    >>> s2 & c == c - {coord}
    True
    >>> s2 & r == r - {coord}
    True
    >>> s2 & q == q - {coord}
    True
    """
    
    coords = column_coords((x, y), include=include)
    coords.extend(row_coords((x, y), include=include))
    coords.extend(quad_coords((x, y), include=include))

    # remove two items of (x, y) in coords (there are three)
    if include:
        coords.remove((x, y))
        coords.remove((x, y))
   
    return coords

if __name__ == '__main__':
    import doctest
    doctest.testmod()
