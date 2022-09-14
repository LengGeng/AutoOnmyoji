import os
from typing import NewType, Tuple

import cv2
import numpy as np
import base64

from utils.ScreenUtils import suitable_screensize

CvImage = NewType("CvImage", np.ndarray)  # cv2 ImageObject(np.ndarray)


def read_image(filepath: str) -> CvImage:
    """
    cv2.imread() 的兼容中文路径的代替方法
    :param filepath: 文件路径
    :return: CvImage cv2图片
    """
    return cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), -1)


def save_image(image: CvImage, filepath: str) -> None:
    """
    保存图片到文件
    :param image: CvImage cv2图片
    :param filepath: 文件路径
    :return:
    """
    name, ext = os.path.splitext(filepath)
    if not ext:
        ext = ".jpg"
    with open(filepath, 'wb') as fp:
        fp.write(cv2bytes(image, ext))


def bytes2cv(image: bytes) -> CvImage:
    """
    二进制图片转cv2图片
    :param image: bytesImage 二进制图片数据
    :return: CvImage cv2图片
    """
    return cv2.imdecode(np.array(bytearray(image), dtype='uint8'), cv2.IMREAD_UNCHANGED)  # 从二进制图片数据中读取


def cv2bytes(image: CvImage, ext: str = ".jpg") -> bytes:
    """
    cv2图片转二进制图片
    :param image: CvImage cv2图片
    :param ext: 图片格式
    :return: bytesImage 二进制图片数据
    """
    _, enc = cv2.imencode(ext, image)
    return np.array(enc).tobytes()


def image_to_base64(image_np: CvImage) -> str:
    """
    将cv2图片转码为base64格式
    image_np: CvImage cv2图片
    Returns: base64编码的数据
    """
    image = cv2.imencode('.png', image_np)[1]
    image_base64 = str(base64.b64encode(image))[2:-1]
    return image_base64


def base64_to_image(base64_code: str) -> CvImage:
    """
    将base64编码解析成cv2图片
    base64_code: base64编码的数据
    Returns: CvImage cv2图片
    """
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.frombuffer(img_data, np.uint8)
    # 转换成opencv可用格式
    image = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    return image


def image_size(image: CvImage) -> Tuple[int, int]:
    """
    获取图片大小
    :param image: CvImage cv2图片
    :return: 图片大小元组
    """
    return image.shape[:2][::-1]


def show(image: CvImage, title: str = 'Image', time: int = 0) -> None:
    """
    显示图片
    :param image: CvImage cv2图片
    :param title: 窗口标题
    :param time: 持续时间
    :return:
    """
    cv2.imshow(title, image)
    cv2.waitKey(time)
    cv2.destroyAllWindows()


def show_adapt(image: CvImage, title: str = 'Image', time: int = 0) -> None:
    """
    显示图片并自适应屏幕大小
    :param image: CvImage cv2图片
    :param title: 窗口标题
    :param time: 持续时间
    :return:
    """
    # 获取图片大小
    size = image_size(image)
    # 获取自适应大小
    adapt_size = suitable_screensize(size)
    # float => int
    adapt_size = tuple(map(int, adapt_size))
    # 改变图片大小
    screen_resize = cv2.resize(image, adapt_size)
    # 显示图片
    show(screen_resize, title, time)


def _test():
    filename = "../test/image/template.jpg"
    # 读取图片
    image = read_image(filename)
    print(type(image))
    # 保存图片
    save_image(image, "../test/image/template.bak.png")
    # ImageToBytes
    cv_bytes = cv2bytes(image)
    # BytesToImage
    cv_image = bytes2cv(cv_bytes)
    save_image(cv_image, "../test/image/template.cv_image.png")
    # ImageToBase64
    image_base64 = image_to_base64(image)
    # Base64ToImage
    base64_image = base64_to_image(image_base64)
    save_image(base64_image, "../test/image/template.base64_image.png")
    # ImageSize
    print(f"{image_size(image)}")
    # show
    show(image)
    # show_adapt
    show_adapt(image)


if __name__ == '__main__':
    _test()
