import string

ALPHABETS = {
    'decimal' : string.digits,
    'hexadecimal' : string.digits + 'abcdef',
    'base62' : string.digits + string.ascii_letters
}


def encode(n, encoding="base62"):
    """

    >>> encode(62, encoding="base62")
    '10'
    >>> encode(61, encoding="base62")
    'Z'
    """
    alphabet = ALPHABETS.get(encoding)
    s = ''
    base = len(alphabet)

    while n:
        n, digit = divmod(n, base)
        s = alphabet[digit] + s

    return s


def decode(s, encoding="base62"):
    """

    >>> decode('0', encoding="base62")
    0
    >>> decode('1', encoding="base62")
    1
    >>> decode('a', encoding="base62")
    10
    >>> decode('A', encoding="base62")
    36
    >>> decode('Z', encoding="base62")
    61
    >>> decode('1A', encoding="base62")
    98
    """
    alphabet = ALPHABETS.get(encoding)
    number = 0
    base = len(alphabet)

    for c in s:
        number *= base
        number += alphabet.index(c)

    return number
