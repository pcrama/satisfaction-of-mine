"Create a unicode sparkline from data in the range [0.0, 1.0]"

import datetime
import itertools
from typing import Iterator

HEIGTHS : str = (
    " "
    "\u2581"  # LOWER ONE EIGHTH BLOCK
    "\u2582"  # LOWER ONE QUARTER BLOCK
    "\u2583"  # LOWER THREE EIGHTHS BLOCK
    "\u2584"  # LOWER HALF BLOCK
    "\u2585"  # LOWER FIVE EIGHTHS BLOCK
    "\u2586"  # LOWER THREE QUARTERS BLOCK
    "\u2587"  # LOWER SEVEN EIGHTHS BLOCK
    "\u2588") # FULL BLOCK

UNDEFINED : str = "\u2591" # LIGHT SHADE

LEFT_SEPARATOR : str = "\u2595" # RIGHT ONE EIGHTH BLOCK
RIGHT_SEPARATOR : str = "\u258F" # LEFT ONE EIGHTH BLOCK

def _valid(x: float) -> bool:
    return 0 <= x <= 1

def format_data(start: str, data: Iterator[float], stop: str) -> str:
    """Create a `graph' representing data in the [0.0, 1.0] range

    The graph is made up by one line of unicode characters.

    NB: when printing this, remember that Python will try to encode this in
    the terminal's character set which (on Windows it's cp1252) maybe doesn't
    support these special characters.  Use sys.stdout.buffer.write to choose
    your own encoding.  See also the C{PYTHONIOENCODING} environment variable.
    """
    left = (start, LEFT_SEPARATOR)
    line = (HEIGTHS[round(x * 8)] if _valid(x) else UNDEFINED for x in data)
    right = (RIGHT_SEPARATOR, stop)
    return "".join(itertools.chain(left, line, right))
