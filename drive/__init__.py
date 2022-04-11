from typing import List

from drive.utils import *
from drive.Driver import Driver
from drive.AdbDriver import AdbDriver

DRIVER_ACTIVE = []


def choose_driver(drivers: List[Driver]) -> Driver:
    """
    从设备列表中选择一个设备进行使用，已经使用的设备无法再次使用
    :param drivers: 设备列表
    :return: 选择的设备
    """
    # 判断是否存在可用设备
    if len(drivers) == 0:
        print("当前无可用设备")
    # 筛选可用设备
    drivers = [driver for driver in drivers if driver.serial not in DRIVER_ACTIVE]
    # 再次判断是否存在可用设备
    if len(drivers) == 0:
        print("当前设备均已被使用")

    print('{:<3}{:<}'.format('序号', '设备编号'))
    for i, driver in enumerate(drivers):
        print(f'{i + 1:<3}{driver}')

    while True:
        try:
            order = int(input('请输入要连接的设备序号：'))
            index = order - 1
            # 排除当输入 0 导致 index=-1 选择最后一个设备
            if index < 0:
                raise IndexError
            driver = drivers[index]
            print(f"您选择的设备是: {driver}")
            if driver.serial in DRIVER_ACTIVE:
                print("当前设备已被使用,请重新选择")
            else:
                DRIVER_ACTIVE.append(driver.serial)
                print("选择设备成功")
            return driver
        except ValueError:
            print("请输入一个整数")
        except IndexError:
            print("输入错误,不存在该设备,请重新选择")


# noinspection PyTypeChecker
def _test_choose_driver():
    choose_driver(AdbDriver.driver_list())


if __name__ == '__main__':
    _test_choose_driver()
