import random
from typing import TypeVar, Union, Tuple, Generator

__all__ = [
    "Pos", "TuplePos", "AnyPos",
    "Scope", "TupleScope", "AnyScope",
    "ProportionPos", "TupleProportionPos", "AnyProportionPos",
    "get_proportion_pos",
    "pos_distance"
]

TuplePos = Tuple[float, float]


class Pos:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Pos({self.x}, {self.y})"

    def __eq__(self, other):
        if isinstance(other, Pos):
            return self.x == other.x and self.y == other.y
        return False

    @property
    def value(self) -> TuplePos:
        return self.x, self.y


AnyPos = TypeVar("AnyPos", Pos, TuplePos)

TupleScope = Tuple[TuplePos, TuplePos]


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

    def __eq__(self, other):
        if isinstance(other, Scope):
            return self.s == other.s and self.e == other.e
        return False

    @property
    def width(self) -> float:
        return abs(self.e.x - self.s.x)

    @property
    def height(self) -> float:
        return abs(self.e.y - self.s.y)

    @property
    def value(self) -> TupleScope:
        return self.s.value, self.e.value

    def randomPos(self) -> Pos:
        """
        从一个范围中随机获取一个点
        :return: 随机点
        """
        return Pos(random.uniform(self.s.x, self.e.x), random.uniform(self.s.y, self.e.y))

    def isin(self, pos: AnyPos) -> bool:
        """
        判断点是否在范围中
        :param pos: 判断的点
        :return: 是否在范围中
        """
        if isinstance(pos, Pos):
            x, y = pos.x, pos.y
        else:
            x, y = pos
        return self.s.x <= x <= self.e.x and self.s.y <= y <= self.e.y


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


def get_proportion_pos(scope: AnyScope, *pro_poss: AnyProportionPos) -> Generator[Pos, None, None]:
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


def pos_distance(a: AnyPos, b: AnyPos) -> float:
    """
    计算两点之间的距离
    :param a: 点a
    :param b: 点b
    :return: 距离
    """
    if isinstance(a, Pos):
        x1, y1 = a.x, a.y
    else:
        x1, y1 = a
    if isinstance(b, Pos):
        x2, y2 = b.x, b.y
    else:
        x2, y2 = b
    # 利用勾股定理求距离
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
