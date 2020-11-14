# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2019/9/24 9:36
# 文件名称  :   adb.PY
# 开发工具  :   PyCharm
import os
import cv2
import time
import random
from subprocess import DEVNULL
from subprocess import PIPE
from subprocess import Popen
from utils.FileUtils import replace_invalid_filename_char

__all__ = ['Adb']


class Adb:
    VERSION = 0.2
    device_id = 999  # 设备唯一id
    device = ''  # 连接设备device
    screen = None  # 屏幕截图
    displays = '1920x1080'  # 屏幕分辨率
    image_path = 'images/screen'  # 截图图片保存路径

    def __init__(self):
        """
        类初始化
        """
        self.devices_list = self.get_devices_list()
        pass

    @staticmethod
    def get_devices_list():
        """
        获取adb设备列表
        :return: adb设备列表
        """
        devices_list = list()
        devices = os.popen("adb devices").read()
        devices_strip = devices.strip('\n').split('\n')
        for devices in devices_strip[1:]:
            devices_list.append(devices.split('\t'))
        return devices_list

    def get_displays(self):
        """
        获取设备分辨率
        :return: 设备分辨率(string)
        """
        dumpsys = os.popen("adb {}shell dumpsys window displays".format(self.device)).read()
        for a in dumpsys.split():
            if a != '':
                if a[:3] == 'cur':
                    return a.split('=')[1]

    def connect_device(self):
        """
        展示devices列表供用户选择
        :return:
        """
        if self.devices_list:
            print("设备列表")
            print('{:<5}{:<15}{:<}'.format('序号', '设备编号', '类型'))
            for i, device in enumerate(self.devices_list):
                print('{:<7}{:<18}{:<}'.format(i, device[0], device[1]))
            if len(self.devices_list) == 1:
                print('当前只有一台设备,已为您自动连接！')
                print('连接的设备是：\t', self.devices_list[0][0])
                self.device = '-s {} '.format(self.devices_list[0][0])
                return True
            while True:
                try:
                    order = int(input('请输入序号选择连接设备：'))
                except ValueError:
                    print('请输入一个整数!')
                    continue

                if order >= len(self.devices_list):
                    print('不存在该设备！请重新选择')
                    continue
                else:
                    print('您选择的设备是：\t', self.devices_list[order][0])
                    self.set_device(self.devices_list[order][0])
                    break
        else:
            print('未能获取到设备,请检查设备连接!')
            return False

    def set_device(self, device, device_id=None):
        self.device = '-s {} '.format(device)
        if device_id is None:
            device_id = device
        self.device_id = replace_invalid_filename_char(str(device_id))

    def screenshot(self):
        """
        截图
        :return:
        """
        # 截屏口令
        cmd_get = 'adb {}shell screencap -p /sdcard/screen_{}.png'.format(self.device, self.device_id)
        # 发送图片口令
        cmd_send = 'adb {}pull sdcard/screen_{}.png {}'.format(self.device, self.device_id, self.image_path)
        # 截屏和发送操作
        # os.system(cmd_get + '&&' + cmd_send)
        proc = Popen(cmd_get + '&&' + cmd_send, shell=True, stdout=PIPE, stderr=DEVNULL, bufsize=-1)
        proc.wait()
        img_rgb = cv2.imread('{}/screen_{}.png'.format(self.image_path, self.device_id))
        # os.remove('screen_{}.png'.format(self.device_id))
        # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        self.screen = img_rgb

    def get_screen(self):
        """
        返回屏幕截图对象(screen)
        :return: 返回截图对象
        """
        if not self.screen:
            self.screenshot()
        return self.screen

    def click(self, pos):
        """
        输入两个二维列表，表示要点击的位置的x坐标，y坐标
        :param pos: 要点击的坐标
        :return:
        """
        command = 'adb {}shell input tap {} {}'.format(self.device, *pos)
        os.system(command)

    def slide(self, pos1, pos2, duration):
        command = 'adb {}shell input swipe {} {} {} {} {}'.format(self.device, *pos1, *pos2, duration)
        os.system(command)

    def touch_event(self, x, y):
        """
        点击事件(显示点击位置)
        :param x: 要点击的纵坐标
        :param y: 要点击的横坐标
        :return:
        """
        event_list = list()
        shell = 'adb {}shell sendevent /dev/input/event5 '.format(self.device)
        event_list.append(shell + '3 57 {}'.format(999 + random.randint(-50, 50)))
        event_list.append(shell + '1 330 1')
        event_list.append(shell + '3 53 {}'.format(x * 10))
        event_list.append(shell + '3 54 {}'.format(y * 10))
        event_list.append(shell + '0 0 0')
        event_list.append(shell + '3 57 4294967295')  # -1
        event_list.append(shell + '1 330 0')
        event_list.append(shell + '0 0 0')
        event = "&&".join(event_list)
        # print(event)
        os.system(event)

    def slide_event(self, x, y, dc='d', distance=200):
        """
        滑动事件(显示滑动位置)
        :param x: 滑动起始点横(x)坐标
        :param y: 滑动起始点纵(y)坐标
        :param dc: 滑动方向
        :param distance: 滑动距离
        :return:
        """
        x = x * 10
        y = y * 10
        distance = distance * 10
        step = distance * 0.1
        if dc == 'u':
            action = 54
            step = step * -1
            a = y
        elif dc == 'd':
            action = 54
            a = y
        elif dc == 'l':
            action = 53
            step = step * -1
            a = x
        elif dc == 'r':
            action = 53
            a = x
        else:
            return False
        event_list = list()
        shell = 'adb {}shell sendevent /dev/input/event5 '.format(self.device)
        event_list.append(shell + '3 57 923')
        event_list.append(shell + '1 330 1')
        event_list.append(shell + '3 53 {}'.format(x))
        event_list.append(shell + '3 54 {}'.format(y))
        event_list.append(shell + '0 0 0')

        i = 0
        while abs(i) < distance * 0.85:
            if i >= 0:
                i = i + step + random.randint(0, 4)
            else:
                i = i + step + random.randint(-4, 0)
            event_list.append(shell + '3 {} {}'.format(action, a + i))
            event_list.append(shell + '0 0 0')

        while abs(i) < distance:
            step = step / 2
            if i >= 0:
                i = i + step + random.randint(0, 2)
            else:
                i = i + step + random.randint(-2, 0)
            event_list.append(shell + '3 {} {}'.format(action, a + i))
            event_list.append(shell + '0 0 0')

        event_list.append(shell + '3 57 4294967295')  # -1
        event_list.append(shell + '1 330 0')
        event_list.append(shell + '0 0 0')
        event = "&&".join(event_list[:len(event_list)])
        os.system(event)


def _test():
    adb = Adb()
    print('devices_list', adb.devices_list)
    adb.connect_device()
    print('设备分辨率：', adb.get_displays())
    adb.screenshot()

    for i in range(1, 10):
        adb.click((i * 10, i * 50))
        adb.touch_event(i * 10, i * 50)
        adb.slide_event(500 + i * 10, 1200, dc='u', distance=1500)


_adb = Adb()
get_devices_list = _adb.get_devices_list
get_displays = _adb.get_displays
connect_device = _adb.connect_device
screenshot = _adb.screenshot
get_screen = _adb.get_screen
click = _adb.click
touch_event = _adb.touch_event
slide_event = _adb.slide_event

if __name__ == '__main__':
    _test()
