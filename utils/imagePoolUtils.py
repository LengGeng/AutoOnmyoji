import os.path
from typing import Dict
from threading import Lock

from utils.imageUtils import CvImage, read_image


class ImagePool:
    def __init__(self, path: str = "./"):
        """
        :param path: 图片池的根路径
        """
        self._path = path
        self.images: Dict[str, CvImage] = {}
        self.__mutex = Lock()

    def get(self, filename):
        # 拼接图片路径
        filepath = os.path.normpath(os.path.join(self._path, filename))
        # 判断图片是否存在, 不存在则读取图片
        if filepath not in self.images:
            self.__mutex.acquire()
            if filepath not in self.images:
                read_image(filepath)
            self.__mutex.release()
        # 返回图片
        return self.images.get(filepath)

    def clear(self):
        """清空图片"""
        self.images.clear()


POOLS: Dict[str, ImagePool] = {}

lock = Lock()


def getImagePool(path: str):
    """
    返回图片池(ImagePool)的单例对象, 每个路径只会有一个图片池
    :param path: 图片池的根路径
    :return:
    """
    key = os.path.normpath(path)
    if key not in POOLS:
        lock.acquire()
        if key not in POOLS:
            POOLS[key] = ImagePool(path)
        lock.release()
    return POOLS[key]


def _test():
    for _ in range(5):
        print(getImagePool("aaa"))
    print('-' * 50)
    for _ in range(5):
        print(getImagePool("bbb"))


if __name__ == '__main__':
    _test()
