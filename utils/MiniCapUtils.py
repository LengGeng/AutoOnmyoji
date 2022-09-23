import socket
import struct
import threading

from utils.QueueUtils import PipeQueue


class Banner:

    def __init__(self):
        self.Version = 0  # 版本信息
        self.Length = 0  # banner长度
        self.Pid = 0  # 进程ID
        self.RealWidth = 0  # 设备的真实宽度
        self.RealHeight = 0  # 设备的真实高度
        self.VirtualWidth = 0  # 设备的虚拟宽度
        self.VirtualHeight = 0  # 设备的虚拟高度
        self.Orientation = 0  # 设备方向
        self.Quirks = 0  # 设备信息获取策略

    def __str__(self):
        message = "Banner [Version=" + str(self.Version) + ", length=" + str(self.Length) + ", Pid=" + str(
            self.Pid) + ", realWidth=" + str(self.RealWidth) + ", realHeight=" + str(
            self.RealHeight) + ", virtualWidth=" + str(self.VirtualWidth) + ", virtualHeight=" + str(
            self.VirtualHeight) + ", orientation=" + str(self.Orientation) + ", quirks=" + str(self.Quirks) + "]"
        return message

    def set_of_bytes(self, data):
        (self.Version,
         self.Length,
         self.Pid,
         self.RealWidth,
         self.RealHeight,
         self.VirtualWidth,
         self.VirtualHeight,
         self.Orientation,
         self.Quirks) = struct.unpack("<2b5ibB", data)


class MinicapStream:
    __instance = {}
    __mutex = threading.Lock()

    def __init__(self, host: str, port: int, queue: PipeQueue):
        self.buffer_size = 4096
        self.__host = host  # socket 主机
        self.__port = port  # socket 端口
        self.banner = Banner()  # 用于存放banner头信息

        self.__pid = 0  # 进程ID
        self.minicapSocket = None
        self.ReadImageStreamTask = None
        self.queue = queue  # 图像数据队列

    @staticmethod
    def getBuilder(host: str, port: int, size=5) -> "MinicapStream":
        """Return a single instance of TestBuilder object """
        key = f"{host}:{port}"
        if key not in MinicapStream.__instance:
            MinicapStream.__mutex.acquire()
            if key not in MinicapStream.__instance:
                MinicapStream.__instance[key] = MinicapStream(host, port, PipeQueue(maxsize=size))
            MinicapStream.__mutex.release()
        return MinicapStream.__instance[key]

    def run(self):
        # 开始执行
        # 启动socket连接
        self.minicapSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 定义socket类型，网络通信，TCP
        self.minicapSocket.connect((self.__host, self.__port))
        print(f"connect to {self.__host}:{self.__port}")
        # return self.ReadImageStream()
        self.ReadImageStreamTask = threading.Thread(target=self.ReadImageStream)
        self.ReadImageStreamTask.daemon = True
        self.ReadImageStreamTask.start()

    def ReadImageStream(self):
        # 读取图片流到队列
        bannerLength = 24
        readBannerBytes = 0

        readFrameBytes = 0
        frameBodyLength = 0
        dataBody = b""
        while True:
            chunk = self.minicapSocket.recv(4096)
            length = len(chunk)
            if not length:
                continue
            cursor = 0
            while cursor < length:
                # just do it
                # 读取 Banner
                if readBannerBytes < bannerLength:
                    if readBannerBytes == 0:
                        self.banner.Version = chunk[cursor]
                    elif readBannerBytes == 1:
                        bannerLength = chunk[cursor]
                        self.banner.Length = bannerLength
                    elif readBannerBytes in [2, 3, 4, 5]:
                        self.banner.Pid += (chunk[cursor] << ((readBannerBytes - 2) * 8)) >> 0
                    elif readBannerBytes in [6, 7, 8, 9]:
                        self.banner.RealWidth += (chunk[cursor] << ((readBannerBytes - 6) * 8)) >> 0
                    elif readBannerBytes in [10, 11, 12, 13]:
                        self.banner.RealHeight += (chunk[cursor] << ((readBannerBytes - 10) * 8)) >> 0
                    elif readBannerBytes in [14, 15, 16, 17]:
                        self.banner.VirtualWidth += (chunk[cursor] << (
                                (readBannerBytes - 14) * 8)) >> 0
                    elif readBannerBytes in [18, 19, 20, 21]:
                        self.banner.VirtualHeight += (chunk[cursor] << (
                                (readBannerBytes - 18) * 8)) >> 0
                    elif readBannerBytes == 22:
                        self.banner.Orientation = chunk[cursor] * 90
                    elif readBannerBytes == 23:
                        self.banner.Quirks = chunk[cursor]
                    cursor += 1
                    readBannerBytes += 1
                    if readBannerBytes == bannerLength:
                        print(self.banner)
                # 读取图片大小数据
                elif readFrameBytes < 4:
                    frameBodyLength = frameBodyLength + ((chunk[cursor] << (readFrameBytes * 8)) >> 0)
                    cursor += 1
                    readFrameBytes += 1
                # 读取图片内容
                else:
                    # print(f"{self.__host}:{self.__port}")
                    # print(f"frame length:{frameBodyLength} length:{length} cursor:{cursor}")
                    if length - cursor >= frameBodyLength:
                        dataBody = dataBody + chunk[cursor:(cursor + frameBodyLength)]
                        if dataBody[0] != 0xFF or dataBody[1] != 0xD8:
                            return
                        self.queue.put(dataBody)
                        # print(f"{self.__host}:{self.__port} add image")
                        # save_file(str(time.time()) + '.jpg', dataBody)
                        cursor += frameBodyLength
                        frameBodyLength = 0
                        readFrameBytes = 0
                        dataBody = b""
                    else:
                        dataBody = dataBody + chunk[cursor:length]
                        frameBodyLength -= length - cursor
                        readFrameBytes += length - cursor
                        cursor = length
