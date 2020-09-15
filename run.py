from Onmyoji import Onmyoji
from utils.adb import Adb
from multiprocessing import Pool
from multiprocessing import freeze_support


class Run:
    def __init__(self):
        self.device_list = self.connect_device()
        self.config = self.get_config()
        p = Pool(len(self.config))
        for data in self.config:
            p.apply_async(self.run, args=(data,))
        print('正在等待所有子进程完成')
        p.close()
        p.join()
        print('所有子流程都已完成')

    @staticmethod
    def run(config):
        try:
            print(config)
            onmyoji = Onmyoji()
            onmyoji.adb.set_device(config['device'])
            onmyoji.__init_logger__()
            if hasattr(onmyoji, config['action']):
                function = getattr(onmyoji, config['action'])
                function(*config['args'])
            else:
                exit("无效的功能函数")
        except Exception as e:
            print(e)

    @staticmethod
    def connect_device():
        devices_list = Adb.get_devices_list()
        device_list = []
        if devices_list:
            print("当前设备列表")
            print('{:<5}{:<15}{:<}'.format('序号', '设备编号', '类型'))
            for i, device in enumerate(devices_list):
                print('{:<7}{:<18}{:<}'.format(i, device[0], device[1]))
            while True:
                if device_list:
                    if input('是否还要添加设备(1 添加/其他 不添加)') == '1':
                        order = input('请输入要添加的设备序号：')
                    else:
                        break
                else:
                    order = input('请输入要连接的设备序号：')

                try:
                    order = int(order)
                except ValueError:
                    print('请输入一个整数!')
                    continue

                if order >= len(devices_list):
                    print('不存在该设备！请重新选择')
                    continue
                elif devices_list[order][0] in set(device_list):
                    print('已添加过该设备!')
                else:
                    print('您选择的设备是：\t', devices_list[order][0])
                    device_list.append(devices_list[order][0])
                    continue
        else:
            print('未能获取到设备,请检查设备连接!')
            exit()
        print(device_list)
        return device_list

    def get_config(self):
        config = []
        fun_list = [
            ['业原火', 'yeyuanhuo', ['请输入贪的数量', '请输入嗔的数量', '请输入痴的数量']],
            ['组队司机', 'zudui', ['请输入开车次数']],
            ['组队乘客', 'chengke', ['请输入上车次数']],
            ['结界突破', 'jiejie', ['请输入上车次数']],
            ['活动', 'huodong', ['请输入次数']]
        ]
        print("功能列表")
        print('{:<5}{:<15}{:<}'.format('序号', '功能', '对应函数'))
        for i, function in enumerate(fun_list):
            print('{:<7}{:<15}{:<}'.format(i, function[0], function[1]))
        for device in self.device_list:
            while True:
                action = input('请输入序号为设备 {} 配置功能'.format(device))
                function = fun_list[int(action)][1]
                print('您选择的是 {} 功能'.format(fun_list[int(action)][0]))
                args = []
                for s in fun_list[int(action)][2]:
                    args.append(int(input(s)))
                config.append({'device': device, 'action': function, 'args': args})
                break
        print(config)
        return config


def main():
    Run()


if __name__ == '__main__':
    freeze_support()
    main()
