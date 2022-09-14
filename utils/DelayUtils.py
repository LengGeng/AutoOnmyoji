import time
import random

# 默认的延迟区间
from typing import List, Tuple

DEFAULT_MOOD = [
    (300, 800),  # energetic: 状态极佳,延迟0.3-0.8s
    (500, 1000),  # joyful: 状态不错,延迟0.5-1.0s
    (800, 1400),  # normal: 状态一般,延迟0.8-1.4s
    (1000, 1800),  # tired: 状态疲劳,延迟1.0-1.8s
    (1500, 2400)  # exhausted: 精疲力尽,延迟1.5-2.4s
]
DEFAULT_INTERVAL = [
    8 * 1000,  # energetic->joyful
    10 * 1000,  # joyful->normal
    15 * 1000,  # normal->tired
    20 * 1000,  # tired->exhausted
    10 * 1000  # exhausted->energetic
]


class MoodDelay:
    """
    模拟符合人类行为状态的点击延迟,时间单位均为毫秒
    """

    def __init__(self, state: int = 0,
                 mood: List[Tuple[int, int]] = None, interval: List[int] = None,
                 system_delay: int = 0):
        """
        初始化
        :param state: 初始状态
        :param mood: 延迟状态列表
        :param interval: 状态切换间隔
        :param system_delay: 设备的点击延迟(毫秒)
        :param state:
        :param mood:
        :param interval:
        :param system_delay:
        """
        if mood is None:
            mood = DEFAULT_MOOD
        if interval is None:
            interval = DEFAULT_INTERVAL
        self.mood = mood
        self.interval = interval
        if len(mood) != len(interval):
            raise ValueError("interval 的长度应为 mood 长度 - 1")
        self.state = state
        self.max_state = len(self.mood) - 1
        self.system_delay = system_delay
        self.timer = time.time()
        self.update_time = self.timer

    def set_state(self, state: int):
        """
        设置状态
        :param state: 状态值,不合理的值会被忽略
        :return:
        """
        if 0 <= state <= self.max_state:
            self.state = state

    def update(self):
        """更新状态"""
        # 更新状态
        new_time = time.time()
        # 检查距离上次更新是否达到足够的间隔时间
        if (new_time - self.update_time) * 1000 > self.interval[self.state]:
            self.update_time = new_time
            if self.state < self.max_state:
                self.state += 1
            else:
                self.state = 0

    def get_mood(self) -> Tuple[int, int]:
        """返回行为状态延迟区间"""
        self.update()
        start, end = self.mood[self.state]
        return self.system_delay + start, self.system_delay + end

    def get_delay(self) -> float:
        """返回行行为状态延迟区间内随机延迟时间"""
        return random.uniform(*self.get_mood())

    def sleep(self):
        """行为状态延迟区间内随机睡眠"""
        time.sleep(self.get_delay() / 1000)

    def __repr__(self):
        """MoodDelay(状态,延迟范围,下一状态间隔范围)"""
        return f"{self.__class__.__name__}{(self.state, *self.get_mood(), self.interval[self.state])}"


def test():
    mood = MoodDelay(
        0,
        [
            (100, 200),
            (200, 400),
            (300, 600),
            (400, 800),
        ],
        [
            2000,
            4000,
            6000,
            8000
        ]
    )
    state = mood.state
    print(f"{mood} at {time.time()}")
    for _ in range(100):
        mood.sleep()
        if state != mood.state:
            state = mood.state
            print(f"{mood} at {time.time()}")


if __name__ == '__main__':
    test()
