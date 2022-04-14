from typing import TypeVar, Tuple

__all__ = ["Pos", "AnyPos", "TuplePos", "Scope", "AnyScope", "TupleScope"]


class Pos:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Pos({self.x}, {self.y})"


TuplePos = Tuple[float, float]
AnyPos = TypeVar("AnyPos", Pos, TuplePos)


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

    @property
    def width(self) -> float:
        return abs(self.e.x - self.s.x)

    @property
    def height(self) -> float:
        return abs(self.e.y - self.s.y)


TupleScope = Tuple[TuplePos, TuplePos]
AnyScope = TypeVar("AnyScope", Scope, Tuple[Pos, Pos], TupleScope)


def _test_any_scope(scope: AnyScope):
    if not isinstance(scope, Scope):
        scope = Scope(*scope)
    print(scope)


def _test_pos():
    pos1 = Pos(x=123, y=456)
    pos2 = Pos(x=147, y=258)
    print(f"{pos1}")
    print(f"{pos2}")
    scope1 = Scope(pos1, pos2)
    print(f"{scope1}")
    scope2 = Scope((100, 120), (200, 240))
    print(f"{scope2}")
    _test_any_scope(scope2)
    _test_any_scope((Pos(100, 100), Pos(1000, 2000)))
    _test_any_scope(((100, 100), (1000, 2000)))


if __name__ == '__main__':
    _test_pos()
