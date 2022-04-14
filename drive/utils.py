from typing import TypeVar, Union, Tuple, Generator

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


class ProportionPos:
    """
    比例坐标
    它表示该点在范围中的比例, 不能单独使用, 必须配合范围返回相应点坐标方可使用
    当值 <1 是表示该点坐标在范围的 100n% 处
    当值 >1 是表示该点坐标在范围的 1/n 处
    例:
      n = 0.4, 该点在范围的 40% 处
      n = 5  , 该点在范围的 1/5(20%) 处
    """

    def __init__(self, x: float, y: float):
        self.x = x if x < 1 else 1 / x
        self.y = y if y < 1 else 1 / y

    def __repr__(self):
        return f"ProportionPos({self.x}, {self.y})"

    def getPos(self, scope: AnyScope):
        if not isinstance(scope, Scope):
            scope = Scope(*scope)

        x = scope.s.x + scope.width * self.x
        y = scope.s.y + scope.height * self.y
        return Pos(x, y)


TupleProportionPos = Union[Tuple[float, float], Tuple[int, int], Tuple[int, float], Tuple[float, int]]
AnyProportionPos = TypeVar("AnyProportionPos", ProportionPos, TupleProportionPos)


def getProportionPos(scope: AnyScope, *pro_poss: AnyProportionPos) -> Generator[Pos, None, None]:
    """
    处理一个范围的批量方法, 它是一个生成器
    :param scope: 范围
    :param pro_poss: 比例坐标点
    :return: 坐标点
    """
    if not isinstance(scope, Scope):
        scope = Scope(*scope)

    for pro_pos in pro_poss:
        if not isinstance(pro_pos, ProportionPos):
            pro_pos = ProportionPos(*pro_pos)

        yield pro_pos.getPos(scope)


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


def _test_pro_pos():
    print("_test_pro_pos")
    pro_pos = ProportionPos(0.5, 5)
    print(f"pro_pos={pro_pos}")
    scope = Scope((0, 0), (1920, 1080))
    print(f"scope={scope}")
    print(f"pro_pos.getPos(scope)={pro_pos.getPos(scope)}")
    print(f"pro_pos.getPos(((0, 0), (1920, 1080)))={pro_pos.getPos(((0, 0), (1920, 1080)))}")

    poss = getProportionPos(scope, (10, 5), (0.1, 20))
    print(f"getProportionPos()={tuple(poss)}")


if __name__ == '__main__':
    _test_pos()
    _test_pro_pos()
