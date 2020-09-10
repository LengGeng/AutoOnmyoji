# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2019/9/30 14:30
# 文件名称  :   log.PY
# 开发工具  :   PyCharm
import os
import time
import logging


class Log(object):
    def __init__(self, logger=None):
        self.LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
        self.DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"  # 日期格式
        self.log_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'log/')
        self.log_name = self.log_path + time.strftime("%Y_%m_%d_yys_log.log")

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')  # 这个是python3的
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        # 创建一个logger
        logging.basicConfig(level=logging.DEBUG, format=self.LOG_FORMAT, datefmt=self.DATE_FORMAT,
                            handlers=[fh, ch])  # 调用
        self.logger = logging.getLogger(logger)
        # 关闭打开的文件
        fh.close()
        ch.close()

    def getlogger(self):
        return self.logger


log = Log().getlogger()
