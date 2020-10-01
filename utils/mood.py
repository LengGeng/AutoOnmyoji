import time
import random


class Mood:
    """
    模拟随机点击随机延迟,每5分钟更换一次,20分钟前逐级递增,20分钟后以随机状态
    energetic:     状态极佳,点击延迟在1.0-1.5s
    joyful:        状态不错,点击延迟在1.3-2.0s
    normal:        状态一般,点击延迟在1.8-2.5s
    tired:         状态疲劳,点击延迟在2.5-3.0s
    exhausted:     精疲力尽,点击延迟在3.0-4.0s
    """
    system_delay = 800  # 模拟器点击延迟,单位毫秒
    default_mood = [
        (1000, 1500),
        (1300, 2000),
        (1800, 2500),
        (2500, 3000),
        (3000, 4000)
    ]  # mood设置
    random_state = 20 * 60  # 开始随机状态的时间,单位分钟
    update_time = 5 * 60  # 状态更新的时间频路,单位分钟

    def __init__(self, state=0):
        self.state = state
        self.max_state = len(self.default_mood) - 1
        self.first_time = time.time()
        self.last_time = self.first_time

    def set_state(self, state):
        """设置状态"""
        self.state = state

    def update_state(self):
        """更新状态"""
        last_time = time.time()
        # 五分钟更新一次状态
        if (last_time - self.last_time) >= self.update_time:
            self.last_time = last_time
            # 20分钟前逐级递增,20分钟后以随机状态
            if (last_time - self.first_time) > self.random_state:
                self.state = random.randint(0, self.max_state)
            else:
                self.state = min(self.state + 1, self.max_state)

    def get_mood(self):
        """返回延迟区间(毫秒)"""
        self.update_state()
        start, end = self.default_mood[self.state]
        return self.system_delay + start, self.system_delay + end

    def get_delay(self):
        """返回状态随机延迟时间(毫秒)"""
        start, end = self.get_mood()
        return random.randint(start, end)

    def mood_sleep(self):
        """状态随机睡眠"""
        time.sleep(self.get_delay() / 1000)
        pass


if __name__ == '__main__':
    mood = Mood()
    while True:
        delay = mood.get_mood()
        print(delay)
        time.sleep(1)
