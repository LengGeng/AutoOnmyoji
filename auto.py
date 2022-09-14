import functools
import random
import time
from numbers import Number
from typing import Callable, Optional, Union, Tuple, List

from stopit import threading_timeoutable

from drives import Driver
from utils import CVUtils
from utils.ImageUtils import CvImage
from utils.DelayUtils import MoodDelay
from utils.PosUtils import Pos, Scope


class Debug:
    def __init__(self, _debug: bool = True):
        self._debug = _debug
        self._proxy_()

    def _proxy_(self, proxy_map: dict = None):
        """
        代理 debug 函数
        在原函数执行前后分别执行前置函数与后置函数
        :param proxy_map: 函数与实际执行函数之间的对应关系 原函数名:实际执行函数[名] 若没有则执行原有函数
        :return:
        """
        if proxy_map is None:
            proxy_map = {}
        # 获取所有的普通方法名
        fun_names = [f_name for f_name in dir(self) if f_name[0] != "_"]
        # 尝试创建代理
        for f_name in fun_names:
            # 获取新的方法名
            proxy_f_name = proxy_map.get(f_name, f_name)
            # 判断是函数还是函数名
            if callable(proxy_f_name):
                func = proxy_f_name
            else:  # 尝试获取方法
                if hasattr(self, proxy_f_name):
                    func = getattr(self, proxy_f_name)
                else:
                    func = getattr(self, f_name)
            # 判断是否是函数
            if callable(func):
                # 生成新方法
                proxy_func = self._debug_(f_name)(func)
                # 覆盖方法
                setattr(self, f_name, proxy_func)

    def _debug_(self, __name__=None):
        """
        为函数创建 debug 代理,执行特定的函数
        在函数之前执行 _{func_name}_before_ 函数,参数为函数的所有参数
            若该参数返回值不为 None,将其返回值覆盖原有参数
        在函数之后执行 _{func_name}_after_ 函数,参数为函数的执行结果
        :param __name__: 函数的原名称,以在装饰器装饰后保持原有名称
        :return:
        """

        def decorator(func: Callable):
            # debug 函数名
            before_f_name = f"_{__name__}_before_"
            after_f_name = f"_{__name__}_after_"
            # 获取函数
            before_func = None
            after_func = None
            if hasattr(self, before_f_name):
                before_func = getattr(self, before_f_name)
            if hasattr(self, after_f_name):
                after_func = getattr(self, after_f_name)

            # print(__name__, before_f_name, after_f_name, before_func, after_func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 获取函数中的 debug 参数
                debug = kwargs.pop("debug", None)
                # 获取不到采用类中的参数
                if debug is None:
                    debug = self._debug

                # 前置函数
                if debug:
                    # 执行前置函数,参数为函数的所有参数
                    # 若返回结果不为None,则视为修改参数
                    if callable(before_func):
                        before_result = before_func(*args, **kwargs)
                        if before_result is not None:
                            args, kwargs = before_result

                # 执行函数
                result = func(*args, **kwargs)

                # 后置函数
                if debug:
                    # 执行前置函数,参数为函数的执行结果
                    if callable(after_func):
                        after_func(result)
                # 返回结果
                return result

            # 更改函数名称
            if __name__:
                wrapper.__name__ = __name__
            return wrapper

        return decorator


class Auto:
    accuracy = 0.95

    def __init__(self, driver: Driver):
        super().__init__()
        self.mood = MoodDelay()
        # 驱动，设备
        self.driver = driver
        self._debug = False

    def delay(self, t: Optional[Union[Number, Tuple[Number, Number]]] = None):
        """
        延迟
        :param t: 延迟的时间(s)
        参数为空时,采用系统合理随机延时
        参数为数字时,睡眠相应时间
        参数为元组时,在两个数字范围内随机睡眠
        :return:
        """
        if t is None:
            self.mood.sleep()
        elif isinstance(t, (int, float)):
            time.sleep(t)
        elif isinstance(t, tuple):
            time.sleep(random.uniform(*t))

    def click(self, pos: Union[Pos, Scope]):
        """
        点击设备相应位置
        :param pos: 位置坐标
        :return:
        """
        if isinstance(pos, Scope):
            pos = pos.randomPos()
        self.driver.click(pos)

    def double_click(self, pos: Union[Pos, Scope], offset: float = 5):
        """
        双击
        :param pos: 点击的坐标
        :param offset: 两次点击之间的位置偏移
        :return:
        """
        if isinstance(pos, Scope):
            original_pos = pos.randomPos()
        else:
            original_pos = pos
        poss = []
        while len(poss) >= 2:
            # 偏移
            offset_pos = (
                original_pos.x + random.uniform(offset * -1, offset),
                original_pos.y + random.uniform(offset * -1, offset),
            )

            if isinstance(pos, Scope):
                # 判断是否在范围中
                if pos.isin(offset_pos):
                    poss.append(offset_pos)
            else:
                poss.append(offset_pos)
        # 点击
        for offset_pos in poss:
            self.click(Pos(*offset_pos))

    def match(self, target: CvImage):
        """
        从屏幕中寻找目标
        :param target: 寻找的目标
        :return: 是否找到目标
        """
        return CVUtils.match(self.driver.screen, target, self.accuracy)

    def match_touch(self, target: CvImage) -> bool:
        """
        从屏幕中寻找目标并点击
        :param target: 寻找的目标
        :return: 是否成功点击
        """
        scope = self.find(target)
        if scope:
            pos = scope.randomPos()
            self.driver.click(pos)
            return True
        return False

    def find(self, target: CvImage) -> Optional[Scope]:
        """
        从屏幕中寻找目标位置
        :param target: 寻找的目标
        :return: 目标位置范围
        """
        result = CVUtils.find(self.driver.screen, target, self.accuracy)
        if result:
            return Scope(*result)

    def find_all(self, target: CvImage) -> List[Scope]:
        """
        从屏幕中寻找目标的多个位置
        :param target: 寻找的目标
        :return: 目标位置范围列表
        """
        results = CVUtils.find_all(self.driver.screen, target, self.accuracy, gap=15)
        return [Scope(*result) for result in results]

    def wait(self, target: CvImage, timeout: float = 10, interval: float = 0.5) -> bool:
        """
        等待直到寻找到目标
        :param target: 寻找的目标
        :param timeout: 超时时间,当超时后不在继续等待
        :param interval: 间隔时间,每次检测等待的时间
        :return: 是否在超时时间内匹配到目标
        """
        # 记录开始时间
        start_time = time.time()
        while True:
            # 截图
            self.driver.screenshot()
            # 匹配
            if self.match(target):
                return True
            # 判断超时
            if (time.time() - start_time) > timeout:
                # 超时则返回结束
                return False
            else:
                # 未超时则进行下次循环
                time.sleep(interval)

    @threading_timeoutable(default=False)
    def wait_quick(self, target: CvImage, interval: float = 0.5):
        """
        等待直到寻找到目标
        该方法与 wait 方法的区别是该方法到达 timeout 指定的时间后会立即退出,而 wait 还需要执行到判断是否超时处才会退出
        :param target: 寻找的目标
        :param interval: 间隔时间,每次检测等待的时间
        :return: 是否在超时时间内匹配到目标
        """
        while True:
            # 截图
            self.driver.screenshot()
            # 匹配
            if self.match(target):
                return True
            # 间隔
            time.sleep(interval)


class AutoDebug(Auto, Debug):
    pass
