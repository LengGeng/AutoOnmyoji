# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2020/4/9 0:04
# 文件名称  :   server.PY
# 开发工具  :   PyCharm
import ssl
import json
from os import path
from Onmyoji import Onmyoji
from urllib import parse
from utils.adb import Adb
from multiprocessing import Process
from webbrowser import open as webopen
from multiprocessing import freeze_support
from http.server import BaseHTTPRequestHandler, HTTPServer

GUI_DIR = 'webgui'
ROOT_DIR = path.join(path.dirname(path.realpath(__file__)), GUI_DIR)
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
}
ACTIVITY = {}


def yysRun(option):
    print("开始执行任务")
    print(option)
    device = option['device'][0]
    fun = 'onmyoji.' + option['fun'][0]
    args = option['args[]'] if 'args[]' in option else []
    onmyoji = Onmyoji()
    onmyoji.adb.set_device(device)
    onmyoji.__init_logger__()
    if args:
        eval(fun)(*args)
    else:
        eval(fun)()


def get_device():
    devices_list = Adb.get_devices_list()
    return {'devices': devices_list}


def screen(device):
    adb = Adb()
    adb.set_device(device)
    adb.image_path = "./{}/screen".format(GUI_DIR)
    adb.screenshot()
    filename = path.join('screen', 'screen_' + device + '.png')
    return filename


def get_active():
    active = []
    print(ACTIVITY)
    if ACTIVITY:
        for device, item in ACTIVITY.items():
            active.append({'device': device, 'fun': item[0]})
    return active


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    Origin = 'https://yys.usaz.cn'

    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        # noinspection PyBroadException
        try:
            # url解码
            url = parse.urlparse(parse.unquote(self.path))
            # 获取url路径
            file_path = url.path
            # url里的参数
            RequestArgs = parse.parse_qs(url.query)
            # print('RequestType: GET')
            # print('URL: ', url)
            # print('URL_PATH: ', file_path)
            # print('RequestArgs: ', RequestArgs)
            # 补充默认文件路径
            if file_path.endswith('/'):
                file_path += 'index.html'
            # 获取文件名及后缀名
            filename, fileExt = path.splitext(file_path)

            if fileExt in CONTENT_TYPE:
                ContentType = CONTENT_TYPE[fileExt]
                try:
                    with open(ROOT_DIR + file_path, 'rb') as f:
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
            url = parse.urlparse(parse.unquote(self.path))
            # 获取url路径
            file_path = url.path
            # url里的参数
            RequestArgs = parse.parse_qs(self.rfile.read(int(self.headers['content-length'])).decode())  # 重点在此步!
            # print('RequestType: POST')
            # print('URL: ', url)
            # print('URL_PATH: ', file_path)
            # print('RequestArgs: ', RequestArgs)
            # 执行任务
            if file_path == '/run':
                device = RequestArgs['device'][0]
                fun = 'yys.' + RequestArgs['fun'][0]
                if device in ACTIVITY:
                    self._sendHttpBody({"code": 1001, "msg": "该设备已有执行的任务!"})
                else:
                    p = Process(target=yysRun, args=(RequestArgs,))
                    ACTIVITY[device] = [fun, p]
                    self._sendHttpBody({"code": 0})
                    p.start()
            # 返回设备
            if file_path == '/device':
                devices = get_device()
                self._sendHttpBody({"code": 0, "data": devices})
            # 截图
            if file_path == '/screen':
                screen_img = screen(RequestArgs['device'][0])
                self._sendHttpBody({"code": 0, "data": {'screen': screen_img}})
            # 活动任务
            if file_path == '/active':
                active = get_active()
                self._sendHttpBody({"code": 0, "data": active})
        except Exception as e:
            print("服务器未知错误: ", e)
            self._sendHttpBody({"code": -1, "msg": "服务器未知错误!"})

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
        if isinstance(data, bytes):
            body = data
        elif isinstance(data, str):
            body = data.encode('utf-8', errors='ignore')
        else:
            body = json.dumps(data).encode('utf-8', errors='ignore')
        self.wfile.write(body)


if __name__ == "__main__":
    freeze_support()
    try:
        server_address = ('127.0.0.1', PORT)
        with HTTPServer(server_address, MyHTTPRequestHandler) as httpd:
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile=GUI_DIR + '/server.key', server_side=True)
            print("HTTP server is starting at port " + repr(PORT) + '...')
            print("Press ^C to quit")
            print("https://127.0.0.1:8080")
            webopen('https://127.0.0.1:8080', new=0, autoraise=True)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
