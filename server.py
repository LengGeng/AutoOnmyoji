# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2020/4/9 0:04
# 文件名称  :   server.PY
# 开发工具  :   PyCharm
import ssl
import json
import psutil
import os.path
import urllib.parse

from drives import MiniDriver
from utils.adb import Adb
from multiprocessing import Process
from webbrowser import open as webopen
from multiprocessing import freeze_support
from run import OnmyojiRun, get_fun
from http.server import BaseHTTPRequestHandler, HTTPServer

GUI_DIR = 'webgui'
ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), GUI_DIR)
print('ROOT_DIR[%s]' % ROOT_DIR)

PORT = 8080
CONTENT_TYPE = {
    '.gif': 'image/gif',
    '.jpg': 'image/jpeg',
    '.htm': 'text/html',
    '.txt': 'text/plain',
    '.css': 'text/css',
    '.html': 'text/html',
    '.json': 'application/json',
    '.png': 'image/png',
    '.ico': 'image/png',
    '.js': 'application/javascript',
    '.avi': 'video/x-msvideo',
    '.ttf': 'font/ttf',
    '.woff': 'font/woff',
}
ACTIVITY = {}


# 暂停进程
def suspendProcess(process: Process):
    pid = process.pid
    print('进程暂停 进程编号 %s ' % pid)
    p = psutil.Process(pid)
    p.suspend()


# 唤醒进程
def wakeProcess(process: Process):
    pid = process.pid
    print('进程恢复 进程编号 %s ' % pid)
    p = psutil.Process(pid)
    p.resume()


# 关闭进程
def finishProcess(process: Process):
    pid = process.pid
    print('进程关闭 进程编号 %s ' % pid)
    process.terminate()


# 解析请求参数
def get_request_params(text: str, content_type: str = None):
    """解析请求参数
    :param text: 参数文本
    :param content_type: Content-Type
    :return:
    """
    if content_type is not None:
        if content_type.startswith("application/json"):
            return json.loads(text)
        elif content_type.startswith("application/x-www-form-urlencoded"):
            return urllib.parse.parse_qs(text)
    return urllib.parse.parse_qs(text)


# 运行任务
def Run(option):
    device = option['device']
    fun = option['fun']
    args = option.get("args") or ()
    kwargs = option.get("kwargs") or {}
    if device in ACTIVITY:
        p: Process = ACTIVITY[device]["process"]
        if p.is_alive():
            return {"code": 1001, "msg": "该设备已有执行的任务!"}

    p = Process(target=OnmyojiRun, args=(device, fun, *args), kwargs=kwargs)
    ACTIVITY[device] = {"fun": fun, "process": p, "suspend": False}
    p.start()
    print("开始执行任务")


# 获取截图
def screen(option):
    """截图
    :param option: 参数
    :return: 截图文件路径
    """
    device = option['device']
    adb = Adb()
    adb.set_device(device, "9999")
    adb.image_path = "./{}/screen".format(GUI_DIR)
    adb.screenshot()
    filename = os.path.join('screen', 'screen_9999.png')
    return filename


# 获取活动任务
def get_active():
    active = []
    print(ACTIVITY)
    if ACTIVITY:
        for device, info in ACTIVITY.items():
            fun = info["fun"]
            process = info["process"]
            suspend = info["suspend"]
            active.append({'device': device, 'fun': fun, "alive": process.is_alive(), "suspend": suspend})
    return active


# 结束任务
def finish_task(option):
    device = option['device']
    if device in ACTIVITY and ACTIVITY[device]["process"].is_alive():
        process: Process = ACTIVITY[device]["process"]
        finishProcess(process)
        return {"data": "success"}
    else:
        return {"code": 500, "mag": "当前设备没有正在执行的任务"}


# 暂停任务
def suspend_task(option):
    device = option['device']
    if device in ACTIVITY and ACTIVITY[device]["process"].is_alive():
        process: Process = ACTIVITY[device]["process"]
        suspend: bool = ACTIVITY[device]["suspend"]
        if not suspend:
            suspendProcess(process)
            ACTIVITY[device]["suspend"] = True
            return {"data": "success"}
    else:
        return {"code": 500, "mag": "当前设备没有正在执行的任务"}


# 唤醒任务
def wake_task(option):
    device = option['device']
    if device in ACTIVITY and ACTIVITY[device]["process"].is_alive():
        process: Process = ACTIVITY[device]["process"]
        suspend: bool = ACTIVITY[device]["suspend"]
        if suspend:
            wakeProcess(process)
            ACTIVITY[device]["suspend"] = False
            return {"data": "success"}
    else:
        return {"code": 500, "mag": "当前设备没有正在执行的任务"}


def get_devices():
    return [[device.serial, "device"] for device in MiniDriver.driver_list()]


# 路由表
ROUTER = {
    "/run": Run,  # 执行任务
    "/device": get_devices,  # 返回设备
    "/screen": screen,  # 截图
    "/active": get_active,  # 活动任务
    "/fun": get_fun,  # 获取功能参数
    "/finish": finish_task,  # 结束任务
    "/suspend": suspend_task,  # 暂停任务
    "/wake": wake_task,  # 唤醒任务
}


class OnmyojiHTTPRequestHandler(BaseHTTPRequestHandler):
    Origin = 'https://yys.usaz.cn'

    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        # noinspection PyBroadException
        try:
            # url解码
            url = urllib.parse.urlparse(urllib.parse.unquote(self.path))
            # 获取url路径
            url_path = url.path
            # url里的参数
            # RequestArgs = get_request_params(url.query)
            # print('RequestType: GET')
            # print('URL: ', url)
            # print('URL_PATH: ', url_path)
            # print('RequestArgs: ', RequestArgs)
            # 补充默认文件路径
            if url_path.endswith('/'):
                url_path += 'index.html'
            # 获取文件名及后缀名
            filename, fileExt = os.path.splitext(url_path)

            if fileExt in CONTENT_TYPE:
                ContentType = CONTENT_TYPE[fileExt]
                try:
                    with open(ROOT_DIR + url_path, 'rb') as f:
                        content = f.read()
                        self._sendHttpBody(content, ContentType)
                except IOError:
                    self.send_error(404, 'File Not Found: %s' % self.path)
        except Exception as e:
            print("服务器未知错误: ", e)
            self._sendHttpBody({"code": -1, "msg": "服务器未知错误!"})

    def do_POST(self):
        # noinspection PyBroadException
        try:
            # url解码
            url = urllib.parse.urlparse(urllib.parse.unquote(self.path))
            # 获取url路径
            url_path = url.path
            # url里的参数
            request_text = self.rfile.read(int(self.headers['content-length'])).decode()  # 重点在此步!
            content_type = self.headers['content-type']
            RequestArgs = get_request_params(request_text, content_type)
            print(f'RequestArgs: {RequestArgs}')

            response = {"code": 0}
            if url_path in ROUTER:
                function = ROUTER[url_path]
                if RequestArgs:
                    data = function(RequestArgs)
                else:
                    data = function()
                if type(data) == dict:
                    response.update(data)
                else:
                    response["data"] = data
                print("response: ", response)
                self._sendHttpBody(response)
            else:
                print("无效的请求")
                # self.send_error(404)
                self._sendHttpBody({"code": 404})
        except Exception as e:
            print("服务器未知错误: ", e)
            self._sendHttpBody({"code": 500, "msg": "服务器未知错误!"})

    def _sendHttpHeader(self, contentType='application/json'):
        origin = self.headers['Origin'] or self.Origin
        self.send_response(200)
        self.send_header('Content-Type', contentType)
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'GET,POST')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def _sendHttpBody(self, data, contentType='application/json'):
        self._sendHttpHeader(contentType)
        body = b''
        if type(data) == bytes:
            body = data
        elif type(data) == str:
            body = data.encode('utf-8', errors='ignore')
        elif type(data) == dict:
            body = json.dumps(data).encode('utf-8', errors='ignore')
        self.wfile.write(body)


if __name__ == "__main__":
    freeze_support()
    try:
        server_address = ('127.0.0.1', PORT)
        with HTTPServer(server_address, OnmyojiHTTPRequestHandler) as httpd:
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile=GUI_DIR + '/server.key', server_side=True)
            print("HTTP server is starting at port " + repr(PORT) + '...')
            print("Press ^C to quit")
            print("https://127.0.0.1:8080")
            webopen('https://127.0.0.1:8080', new=0, autoraise=True)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
