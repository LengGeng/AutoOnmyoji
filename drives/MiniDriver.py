import os.path
import time
from subprocess import Popen

from drives.AdbDriver import AdbDriver
from settings import LIBS_PATH
from utils.ImageUtils import bytes2cv
from utils.MiniCapUtils import MinicapStream


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
        self._check_minicap_start()
        self._forward_minicap()
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
        self.device.push(minicap_path, "/data/local/tmp/minicap")
        self.device.push(minicap_so_path, "/data/local/tmp/minicap.so")
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
        self.minicap_log_path = os.path.join(self.log_dir, "minicap.log")
        self.logger.debug(f"minicap_log_path:{self.minicap_log_path}")
        with open(self.minicap_log_path, "ab") as fp:
            self.minicap_popen = Popen(start_minicap_server_cmd, stdout=fp, stderr=fp)
            # 等待服务启动完成
            self.logger.info("wait for the minicap serve to startup")
            time.sleep(2)

    def _check_minicap_start(self):
        self.logger.debug("_check_minicap_start start")
        with open(self.minicap_log_path) as fp:
            lines = fp.readlines()
            if len(lines) > 8:
                content = "".join(lines[-8:])
            else:
                content = "".join(lines)
            if "Server start" in content:
                # 启动成功
                self.logger.info("minicap serve startup complete")
            else:
                if "Aborted" in content:
                    # 启动失败
                    self.logger.info("minicap serve startup failed")
                    #  尝试解决 Vector<> have different types 错误
                    if "Vector<> have different types" in content:
                        self._handle_vector_error()
                        return
                else:
                    self.logger.info("minicap serve startup exception")
                exit(1)

    def _handle_vector_error(self):
        self.logger.debug("_handle_vector_error start")
        SupportedBrand = ["XIAOMI", "VIVO", "LG"]
        self.logger.debug(self.brand)
        if self.brand in SupportedBrand:
            supported_vector_minicap_so_path = os.path.abspath(
                f"{LIBS_PATH}/stf/vector_error/{self.brand}/android-{self.sdk_version}/{self.abi}/minicap.so"
            )
            if os.path.isfile(supported_vector_minicap_so_path):
                self.logger.debug("try handle vector error")
                self.logger.debug(f"supported_vector_minicap_so_path:{supported_vector_minicap_so_path}")
                # 发送新的 minicap
                self.device.push(supported_vector_minicap_so_path, "/data/local/tmp/minicap.so")
                self.logger.debug("try restart minicap")
                self._start_minicap()
                return
        # 无法处理
        self.logger.debug("try handle vector error but it is an unsupported brand")

    def _forward_minicap(self):
        # 代理
        self.logger.debug("_forward_minicap start")
        self.minicap_port = self.device.forward_port("localabstract:minicap")
        self.logger.debug(f"minicap forward port {self.minicap_port}")
        self.logger.debug("_start_minicap finish")

    def _read_minicap_stream(self):
        self.logger.debug("_read_minicap_stream start")
        self.minicap_stream = MinicapStream.getBuilder("127.0.0.1", self.minicap_port)
        self.minicap_stream.run()
        self.banner = self.minicap_stream.banner
        self.screen_queue = self.minicap_stream.queue
        self.logger.debug(f"minicap.banner:{self.banner}")
        self.logger.debug("_read_minicap_stream finish")

    def screenshot(self) -> None:
        # self.logger.debug(f"driver screenshot start")
        self._screen = bytes2cv(self.screen_queue.get())
        # self.logger.debug(f"driver screenshot finish")

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
