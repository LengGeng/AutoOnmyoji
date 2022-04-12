import os.path
from datetime import date

DATE = date.today()

LOG_PATH = os.path.join(os.path.dirname(__file__), "log")  # 日志目录
LIBS_PATH = os.path.join(os.path.dirname(__file__), "libs")  # 库目录
SCREEN_PATH = os.path.join(os.path.dirname(__file__), "images/screen")  # 截图目录
