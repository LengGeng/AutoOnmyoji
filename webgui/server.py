# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2020/4/9 0:04
# 文件名称  :   server.PY
# 开发工具  :   PyCharm
import os
import ssl
import json
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
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


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    Origin = 'https://yys.usaz.cn'

    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):
        # url解码
        url = parse.urlparse(parse.unquote(self.path))
        print('URL:', url)
        # 获取url路径
        file_path = url.path
        print('URL_PATH:', file_path)
        # url里的参数
        RequestArgs = parse.parse_qs(url.query)
        print('RequestArgs:', RequestArgs)
        # 补充默认文件路径
        if file_path.endswith('/'):
            file_path += 'index.html'
        # 获取文件名及后缀名
        filename, fileExt = os.path.splitext(file_path)

        if fileExt in CONTENT_TYPE:
            ContentType = CONTENT_TYPE[fileExt]
            try:
                with open(ROOT_DIR + file_path, 'rb') as f:
                    content = f.read()
                    self._sendHttpBody(content, ContentType)
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)

    def _sendHttpHeader(self, contentType='application/json'):
        origin = self.headers['Origin'] or self.Origin
        self.send_response(200)
        self.send_header('Content-Type', contentType)
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'GET,POST')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def _sendHttpBody(self, data, contentType=None):
        if contentType:
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
    try:
        server_address = ('127.0.0.1', PORT)
        with HTTPServer(server_address, MyHTTPRequestHandler) as httpd:
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile='server.key', server_side=True)
            print("HTTP server is starting at port " + repr(PORT) + '...')
            print("Press ^C to quit")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
