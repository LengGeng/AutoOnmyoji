# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2019/9/25 14:32
# 文件名称  :   functions.PY
# 开发工具  :   PyCharm
import time
import random


def get_random_pos(s, e):
    """
    s、e为两个坐标位置，元组  产生一个在c1、c2坐标点内的随机坐标位置
    :param s: 起始坐标
    :param e: 结束坐标
    :return: 随机坐标点
    """
    x = random.uniform(s[0], e[0])
    y = random.uniform(s[1], e[1])
    return x, y


def random_time(a, b):
    """
    产生a,b间的随机时间延迟
    :param a:  最小随机延迟时间
    :param b:  最大随机延迟时间
    :return:
    """
    time.sleep(random.uniform(a, b))


def choice(seq):
    return random.choice(seq)
