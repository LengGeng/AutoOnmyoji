import logging

CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

DEFAULT_LEVEL = INFO
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# 日志级别 时间 文件名[行号]函数名 错误信息
LOG_FORMAT = "%(levelname)s %(asctime)s %(filename)s[%(lineno)d]<%(funcName)s> %(message)s"


class LogUtils:
    def __init__(self, name, level: int = None, log_format: str = None, date_format: str = None,
                 default_handler: bool = True, filename: str = None, ):
        """
        日志工具类初始化
        :param name: 日志器名称
        :param level: 全局日志级别
        :param log_format: 日志格式
        :param date_format: 日期格式
        :param default_handler: 是否添加默认处理器(控制台)
        :param filename: 文件路径,若存在则会创建 file 日志处理器
        """
        # 默认参数
        if level is None:
            level = DEFAULT_LEVEL
        if log_format is None:
            log_format = LOG_FORMAT
        if date_format is None:
            date_format = DATE_FORMAT

        self._level = level
        self._log_format = log_format
        self._date_format = date_format
        self._sh_flag = None
        self._file_flag = None

        # 创建 logger 对象
        self._logger = logging.getLogger(name)
        # 设置日志输出等级总开关
        self._logger.setLevel(level)
        # 默认控制台日志
        if default_handler:
            self.add_sh_handler()
        # 文件日志
        if filename:
            self.add_file_handler(filename)

    def add_handler(self, handler: "logging.Handeler", level: int = None,
                    log_format: str = None, date_format: str = None):
        """
        处理日志处理器 handler 并添加到 logger 中
        :param handler: 日志处理器 Handler
        :param level: 日志级别
        :param log_format: 日志格式
        :param date_format: 日期格式
        :return:
        """
        # 默认参数
        if level is None:
            level = self._level
        if log_format is None:
            log_format = self._log_format
        if date_format is None:
            date_format = self._date_format
        # 统一日志输出格式
        formatter = logging.Formatter(log_format, date_format)
        # 处理
        # 设置日志级别
        handler.setLevel(level)
        # 设置日志格式
        handler.setFormatter(formatter)
        # 添加 handler 到 logger 中
        self._logger.addHandler(handler)

    def add_sh_handler(self, level: int = None, log_format: str = None, date_format: str = None):
        """
        添加控制台日志处理器
        :param level: 日志级别
        :param log_format: 日志格式
        :param date_format: 日期格式
        :return:
        """
        # 检查是否重复创建
        if self._sh_flag is None:
            # 创建控制台实例
            sh = logging.StreamHandler()
            # 处理添加日志文件实例
            self.add_handler(sh, level, log_format, date_format)
            # 销毁资源
            sh.close()
            # 标记创建
            self._sh_flag = True
        # 返回 self 支持链式调用
        return self

    def add_file_handler(self, filename: str, level: int = None, log_format: str = None, date_format: str = None):
        """
        添加文件日志处理器
        :param filename: log 文件路径
        :param level: 日志级别
        :param log_format: 日志格式
        :param date_format: 日期格式
        :return:
        """
        # 检查是否重复创建
        if self._file_flag is None:
            # 创建日志文件实例
            fh = logging.FileHandler(filename, mode='a', encoding='utf-8')
            # 处理添加日志文件实例
            self.add_handler(fh, level, log_format, date_format)
            # 销毁资源
            fh.close()
            # 标记创建
            self._file_flag = True
        # 返回 self 支持链式调用
        return self

    def getLogger(self):
        """
        返回日志对象
        :return:
        """
        return self._logger
