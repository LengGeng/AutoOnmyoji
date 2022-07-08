import os.path
import time
from subprocess import Popen

from drive.AdbDriver import AdbDriver
from settings import LIBS_PATH
from utils.LoopQueue import LoopQueue
from utils.MiniCapUtils import MinicapStream
from utils.imageUtils import bytes2cv


class MiniDriver(AdbDriver):

    def __init__(self, serial: str):
        super().__init__(serial)

    def _init_(self):
        super(MiniDriver, self)._init_()
        self._init_minicap_()

    def _init_system_info_(self):
        super()._init_system_info_()
        # 获取系统参数
        self.abi = self.device.getprop("ro.product.cpu.abi")
        self.sdk_version = self.device.getprop("ro.build.version.sdk")
        self.logger.debug(f"abi:{self.abi}, sdk_version:{self.sdk_version}")

    def _init_minicap_(self):
        self.logger.debug("_init_minicap_")
        self._send_minicap()
        self._start_minicap()
        self._read_minicap_stream()

    def _send_minicap(self):
        self.logger.debug("_send_minicap start")
        # 获取 minicap 文件位置
        minicap_path = os.path.abspath(f"{LIBS_PATH}/stf/{self.abi}/minicap")
        minicap_so_path = os.path.abspath(
            f"{LIBS_PATH}/stf/minicap-shared/aosp/libs/android-{self.sdk_version}/{self.abi}/minicap.so"
        )
        self.logger.debug(f"minicap_path:{minicap_path}")
        self.logger.debug(f"minicap_so_path:{minicap_so_path}")
        # 发送 minicap
        self.device.push(minicap_path, "/data/local/tmp/")
        self.device.push(minicap_so_path, "/data/local/tmp/")
        self.logger.debug("_send_minicap finish")

    def _start_minicap(self):
        self.logger.debug("_start_minicap start")
        # 获取屏幕大小
        # wm_size = self.device.shell("wm size").split(": ")[1]
        # window_size = device.window_size()
        # window_size = f"{window_size.width}x{window_size.height}"
        # window_size = wm_size
        # 更改目录权限以执行
        self.device.shell("chmod 777 /data/local/tmp/*")
        # 执行
        start_minicap_server_cmd = f"adb -s {self._serial} shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P {self.displays}@{self.displays}/0"
        self.logger.debug(f"start_minicap_server_cmd:{start_minicap_server_cmd}")
        # 日志
        minicap_log_path = os.path.join(self.log_dir, "minicap.log")
        self.logger.debug(f"minicap_log_path:{minicap_log_path}")
        with open(minicap_log_path, "ab") as fp:
            self.minicap_popen = Popen(start_minicap_server_cmd, stdout=fp, stderr=fp)
            # 等待服务启动完成
            self.logger.info("wait for the minicap serve to startup")
            time.sleep(2)
            self.logger.info("minicap serve startup complete")
        # 代理
        self.minicap_port = self.device.forward_port("localabstract:minicap")
        self.logger.debug(f"minicap forward port {self.minicap_port}")
        self.logger.debug("_start_minicap finish")

    def _read_minicap_stream(self):
        self.logger.debug("_read_minicap_stream start")
        self.screen_queue = LoopQueue()
        self.minicap_stream = MinicapStream("127.0.0.1", self.minicap_port, self.screen_queue)
        self.minicap_stream.run()
        self.banner = self.minicap_stream.banner
        self.logger.debug(f"minicap.banner:{self.banner}")
        self.logger.debug("_read_minicap_stream finish")

    def screenshot(self) -> None:
        self.logger.debug(f"driver screenshot start")
        self._screen = bytes2cv(self.screen_queue.get())
        self.logger.debug(f"driver screenshot finish")

    def __del__(self):
        if self.minicap_popen:
            self.logger.debug("minicap server close")
            self.minicap_popen.kill()


if __name__ == '__main__':
    import cv2

    adb_device = MiniDriver.driver_list()[0]
    if adb_device:
        driver = MiniDriver(adb_device.serial)
        while True:
            driver.screenshot()
            cv2.imshow("Image", driver.screen)
            cv2.waitKey(1)
