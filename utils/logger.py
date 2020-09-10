import logging


# 获取logger对象
def get_logger(filename="log.log"):
    # [时间] [文件名 - 函数名 - 行号] [日志级别] [错误信息]
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    handlerFormatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(filename)s-%(funcName)s-%(lineno)d %(message)s', datefmt=DATE_FORMAT
    )
    consoleFormat = logging.Formatter('%(asctime)s\t\t%(message)s', datefmt=DATE_FORMAT)

    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)

    # 文件日志输出
    handler = logging.FileHandler(filename, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(handlerFormatter)
    # 控制台日志输出
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(consoleFormat)

    logger.addHandler(handler)
    logger.addHandler(console)
    return logger
