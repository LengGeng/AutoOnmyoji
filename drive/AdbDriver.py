import os.path
from subprocess import Popen, PIPE, DEVNULL
from typing import List

import cv2
import adbutils

from drive import Driver, Pos, AnyPos, Scope, AnyScope
from settings import SCREEN_PATH

BRANDS = ["MEIZU", "XIAOMI", "VIVO", "LG"]


class AdbDriver(Driver):

    def __init__(self, serial: str):
        self.device = adbutils.adb.device(serial)
        # self.sync = adbutils.adb.sync(serial)
        super().__init__(serial)

    def _init_(self):
        super(AdbDriver, self)._init_()
        self._init_window_size_()

    def _start_(self):
        self.logger.info("driver start")
        self.screenshot()

    def _init_window_size_(self):
        # noinspection PyProtectedMember
        w, h = self.device._raw_window_size()
        rotation = self.device.rotation()
        self.width, self.height = (w, h) if rotation % 2 == 0 else (h, w)
        self.logger.debug(f"driver init WindowSize({self.displays})")

    def _init_brand_(self):
        # 获取设备指纹
        fingerprint = self.device.getprop("ro.vendor.build.fingerprint").upper()
        # 判断是都是可以识别的型号
        for BRAND in BRANDS:
            if BRAND in fingerprint:
                self.brand = BRAND
        else:
            # 不支持的机型
            self.brand = None

    @staticmethod
    def driver_list() -> List[adbutils.AdbDevice]:
        """
        获取可用的设备列表
        :return:
        """
        return adbutils.adb.device_list()

    def screenshot(self) -> None:
        self.logger.debug(f"driver screenshot start")
        screen_filename = f"{self._serial}.png"
        screen_filepath = os.path.normpath(os.path.join(SCREEN_PATH, screen_filename))
        screencap_cmd = f"adb -s {self._serial} shell screencap -p /sdcard/{screen_filename}"
        pull_cmd = f"adb -s {self._serial} pull /sdcard/{screen_filename} {SCREEN_PATH}"
        # TODO 更换实现方式 Popen -> adbutils
        Popen(screencap_cmd + '&&' + pull_cmd, shell=True, stdout=PIPE, stderr=DEVNULL, bufsize=-1).wait()
        img_rgb = cv2.imread(screen_filepath)
        self._screen = img_rgb
        self.logger.debug(f"driver screenshot finish")

    def click(self, pos: AnyPos) -> None:
        if not isinstance(pos, Pos):
            pos = Pos(*pos)
        self.device.shell(f"input tap {pos.x} {pos.y}")
        self.logger.debug(f"driver click at ({pos.x}, {pos.y})")

    def swipe(self, scope: AnyScope, duration: int) -> None:
        if not isinstance(scope, Scope):
            scope = Scope(*scope)
        s, e = scope.s, scope.e
        self.device.shell(f"input swipe {s.x} {s.y} {e.x} {e.y} {duration}")
        self.logger.debug(f"driver swipe {duration}ms from ({s.x}, {s.y}) to ({e.x}, {e.y})")


if __name__ == '__main__':
    adb_drive = AdbDriver("emulator-5560")
    print(adb_drive.displays)
    # cv2.imshow("Image", adb_drive.screen)
    # cv2.waitKey(0)
    for i in range(5):
        # adb_drive.click(Pos(100, 100))
        adb_drive.swipe(Scope(Pos(100, 100), Pos(600, 100)), 10)
