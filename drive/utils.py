from typing import TypeVar, Tuple

__all__ = ["Pos", "AnyPos", "Scope"]


class Pos:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Pos({self.x}, {self.y})"


AnyPos = TypeVar("AnyPos", Pos, Tuple[float, float])


class Scope:
    def __init__(self, s: AnyPos, e: AnyPos):
        if not isinstance(s, Pos):
            s = Pos(*s)
        if not isinstance(e, Pos):
            e = Pos(*e)
        self.s = s
        self.e = e

    def __repr__(self):
        return f"Scope(({self.s.x}, {self.s.y}), ({self.e.x}, {self.e.y}))"


def _test_pos():
    pos1 = Pos(x=123, y=456)
    pos2 = Pos(x=147, y=258)
    print(f"{pos1}")
    print(f"{pos2}")
    scope1 = Scope(pos1, pos2)
    print(f"{scope1}")
    scope2 = Scope((100, 120), (200, 240))
    print(f"{scope2}")


if __name__ == '__main__':
    _test_pos()
