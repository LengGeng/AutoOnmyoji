import os.path
from subprocess import Popen, PIPE, DEVNULL
from typing import List

import cv2
import adbutils

from drive import Driver, Pos, Scope
from settings import SCREEN_PATH


class AdbDriver(Driver):

    def __init__(self, serial: str):
        self.device = adbutils.adb.device(serial)
        # self.sync = adbutils.adb.sync(serial)
        super().__init__(serial)

    def _init_(self):
        self._init_window_size_()
        self.screenshot()

    def _init_window_size_(self):
        # noinspection PyProtectedMember
        w, h = self.device._raw_window_size()
        rotation = self.device.rotation()
        self.width, self.height = (w, h) if rotation % 2 == 0 else (h, w)

    @staticmethod
    def driver_list() -> List[adbutils.AdbDevice]:
        """
        获取可用的设备列表
        :return:
        """
        return adbutils.adb.device_list()

    def screenshot(self) -> None:
        screen_filename = f"{self._serial}.png"
        screen_filepath = os.path.normpath(os.path.join(SCREEN_PATH, screen_filename))
        screencap_cmd = f"adb -s {self._serial} shell screencap -p /sdcard/{screen_filename}"
        pull_cmd = f"adb -s {self._serial} pull /sdcard/{screen_filename} {SCREEN_PATH}"
        # TODO 更换实现方式 Popen -> adbutils
        Popen(screencap_cmd + '&&' + pull_cmd, shell=True, stdout=PIPE, stderr=DEVNULL, bufsize=-1).wait()
        img_rgb = cv2.imread(screen_filepath)
        self._screen = img_rgb

    def click(self, pos: Pos) -> None:
        self.device.shell(f"input tap {pos.x} {pos.y}")

    def swipe(self, scope: Scope, duration: int) -> None:
        s, e = scope.s, scope.e
        self.device.shell(f"input swipe {s.x} {s.y} {e.x} {e.y} {duration}")


if __name__ == '__main__':
    adb_drive = AdbDriver("emulator-5560")
    print(adb_drive.displays)
    # cv2.imshow("Image", adb_drive.screen)
    # cv2.waitKey(0)
    for i in range(5):
        # adb_drive.click(Pos(100, 100))
        adb_drive.swipe(Scope(Pos(100, 100), Pos(600, 100)), 10)
