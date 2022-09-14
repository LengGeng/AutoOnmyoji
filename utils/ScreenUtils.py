import ctypes
from typing import Tuple

user32 = ctypes.windll.user32


def get_screensize() -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    获取屏幕大小
    :return: 屏幕大小,真实屏幕大小
    """
    # ref: http://www.dovov.com/python-199.html
    # import win32api, win32con
    # win32api.GetSystemMetrics(win32con.SM_CXSCREEN)  # 获得屏幕分辨率X轴
    # win32api.GetSystemMetrics(win32con.SM_CYSCREEN)  # 获得屏幕分辨率Y轴

    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    user32.SetProcessDPIAware()
    physicalsScreensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize, physicalsScreensize


def adapt_scaling(original_size: Tuple[float, float], adapt_size: Tuple[float, float]) -> Tuple[float, float]:
    """适应缩放
    原大小 在 目标大小 中最大的等比例大小
    :param original_size: 原本大小
    :param adapt_size: 目标大小
    :return: 适应的大小
    """
    original_w, original_h = original_size
    adapt_w, adapt_h = adapt_size
    ratio_w = adapt_w / original_w
    ratio_h = adapt_h / original_h
    ratio = min(ratio_w, ratio_h)
    return original_w * ratio, original_h * ratio


def suitable_screensize(size: Tuple[float, float]) -> Tuple[float, float]:
    """
    根据屏幕大小返回投屏合适的大小
    :param size: 投屏图片的大小
    :return: 合适的大小
    """
    _, (width, height), = get_screensize()
    adapt_size = width * 0.5, height * 0.75
    return adapt_scaling(size, adapt_size)


if __name__ == '__main__':
    print(get_screensize())
    print(adapt_scaling((250, 500), (900, 600)))
    print(suitable_screensize((2232, 1080)))
