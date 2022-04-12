from drive import MiniDriver, choose_driver
from utils.docs import Docs
from Onmyoji import Onmyoji
from multiprocessing import Pool
from multiprocessing import freeze_support


def OnmyojiRun(serial, fun, *args, **kwargs):
    try:
        onmyoji = Onmyoji(MiniDriver(serial))
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


class Run:
    def __init__(self):
        self.FUN_LIST = get_fun()

    def run(self):
        # 循环获取配置
        configs = []
        while True:
            # noinspection PyTypeChecker
            driver = choose_driver(MiniDriver.driver_list())
            if driver is None:
                break
            config = self.get_config(driver.serial)
            configs.append(config)
            if (not self.devices) or input('是否还要添加设备(1 添加/其他 不添加)') != '1':
                break
        if not configs:
            exit('未能获取到设备,请检查设备连接!')
        # 执行
        p = Pool(len(configs))
        for config in configs:
            device, fun, kwargs = config["device"], config["fun"], config["kwargs"]
            p.apply_async(OnmyojiRun, args=(device, fun), kwds=kwargs)
        print('正在等待所有子进程完成')
        p.close()
        p.join()
        print('所有子流程都已完成')

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
