from utils.adb import Adb
from utils.docs import Docs
from Onmyoji import Onmyoji
from multiprocessing import Pool
from multiprocessing import freeze_support


def OnmyojiRun(device, fun, *args, **kwargs):
    try:
        onmyoji = Onmyoji()
        onmyoji.adb.set_device(device)
        onmyoji.init_logger()
        if hasattr(onmyoji, fun):
            function = getattr(onmyoji, fun)
            function(*args, **kwargs)
        else:
            print("无效的功能函数")
    except Exception as e:
        print(e)


def get_fun():
    return Docs(Onmyoji).getall()


def get_devices():
    return [device for device in Adb.get_devices_list() if device[1] == "device"]


class Run:
    def __init__(self):
        self.devices = get_devices()
        if not self.devices:
            exit('未能获取到设备,请检查设备连接!')
        self.FUN_LIST = get_fun()

    def run(self):
        # 循环获取配置
        configs = []
        while True:
            device = self.connect_device()
            config = self.get_config(device)
            configs.append(config)
            if (not self.devices) or input('是否还要添加设备(1 添加/其他 不添加)') != '1':
                break
        # 执行
        p = Pool(len(configs))
        for config in configs:
            device, fun, kwargs = config["device"], config["fun"], config["kwargs"]
            p.apply_async(OnmyojiRun, args=(device, fun), kwds=kwargs)
        print('正在等待所有子进程完成')
        p.close()
        p.join()
        print('所有子流程都已完成')

    # 连接设备
    def connect_device(self):
        print("当前设备列表")
        print('{:<5}{:<15}{:<}'.format('序号', '设备编号', '类型'))
        for i, device in enumerate(self.devices):
            print('{:<7}{:<17}{:<}'.format(i, device[0], device[1]))
        while True:
            try:
                order = int(input('请输入要连接的设备序号：'))
                device = self.devices[order][0]
                self.devices.pop(order)
                print(f"您选择的设备是: {device}")
                return device
            except ValueError:
                print("请输入一个整数")
            except IndexError:
                print("输入错误,不存在该设备,请重新选择")

    # 获取设备配置
    def get_config(self, device):
        print("功能列表")
        print('{:<5}{:<15}{:<}'.format('序号', '功能', '对应函数'))
        for i, func in enumerate(self.FUN_LIST):
            print('{:<5}{:<18}{:<}'.format(i, func["name"], func["function"]))
        while True:
            try:
                order = int(input(f"请为设备 {device} 配置功能"))
                func = self.FUN_LIST[order]
                print('您选择的是 {} 功能'.format(func["name"]))
                kwargs = {}
                for arg, arg_info in func["args"].items():
                    while True:
                        try:
                            kwargs[arg] = int(input(arg_info["desc"]))
                            break
                        except ValueError:
                            print("请输入一个整数")
                return {'device': device, 'fun': func["function"], 'kwargs': kwargs}
            except ValueError:
                print("请输入一个整数")
            except IndexError:
                print("输入错误,不存在该功能,请重新选择")


def _test():
    Run().run()


if __name__ == '__main__':
    freeze_support()
    _test()
