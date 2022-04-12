import os.path
from typing import Optional, Tuple

from drive.utils import AnyPos, AnyScope
from settings import LOG_PATH, DATE
from utils.FileUtils import replace_invalid_filename_char, check_dirs
from utils.imageUtils import CvImage
from utils.logger import get_logger

Screen = CvImage


class Driver:
    """
    设备驱动类，包含设备驱动的必要方法。所有驱动都应该继承并重写该类的方法。
    """

    def __init__(self, serial: str):
        """
        一个设备应该包含以下属性
        :param serial: 设备标识，设备的唯一ID
        """
        self._serial: str = serial
        self._screen: Optional[Screen] = None  # 屏幕截图
        self.width: int = 0  # 设备宽度
        self.height: int = 0  # 设备高度
        # 进行初始化
        self._init_()
        self._start_()

    def _init_(self):
        """
        初始化函数
        :return:
        """
        self._init_log_()
        pass

    def _init_log_(self):
        self.log_dir = os.path.join(LOG_PATH, replace_invalid_filename_char(self._serial), str(DATE))
        check_dirs(self.log_dir)
        log_file_path = os.path.join(self.log_dir, "driver.log")
        self.logger = get_logger(log_file_path)
        self.logger.debug("driver init log")

    def _start_(self):
        """
        开始函数
        :return:
        """
        pass

    def screenshot(self) -> None:
        """
        设备截图，并将截图保存在 _screen 中
        :return:
        """
        pass

    def click(self, pos: AnyPos) -> None:
        """
        点击
        :param pos: 点击的坐标
        :return:
        """
        pass

    def swipe(self, scope: AnyScope, duration: int) -> None:
        """
        滑动
        :param scope: 滑动的范围，从坐标1滑动到坐标2
        :param duration: 滑动持续的时间
        :return:
        """
        pass

    @property
    def serial(self) -> str:
        """
        返回设备标识
        :return:
        """
        return self._serial

    @property
    def size(self) -> Tuple[int, int]:
        """
        屏幕大小、屏幕分辨率的元组形式
        :return:
        """
        return self.width, self.height

    @property
    def displays(self) -> str:
        """
        屏幕大小、屏幕分辨率的元组形式
        :return:
        """
        return f"{self.width}x{self.height}"

    # noinspection PyTypeChecker
    @property
    def screen(self) -> Screen:
        """
        返回设备截图
        :return:
        """
        if self._screen is None:
            self.screenshot()
        return self._screen


if __name__ == '__main__':
    driver = Driver("emulator-5560")
    print(driver.serial)
