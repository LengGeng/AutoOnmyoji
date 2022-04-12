from typing import NewType

import cv2
import numpy as np
import base64

CvImage = NewType("CvImage", np.ndarray)  # cv2 ImageObject(np.ndarray)


def read_image(filepath: str) -> CvImage:
    """
    cv2.imread() 的兼容中文路径的代替方法
    :param filepath: 文件路径
    :return: CvImage cv2图片
    """
    return cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), -1)


def bytes2cv(image: bytes) -> CvImage:
    """
    二进制图片转cv2图片
    :param image: bytesImage 二进制图片数据
    :return: CvImage cv2图片
    """
    return cv2.imdecode(np.array(bytearray(image), dtype='uint8'), cv2.IMREAD_UNCHANGED)  # 从二进制图片数据中读取


def cv2bytes(image: CvImage) -> bytes:
    """
    cv2图片转二进制图片
    :param image: CvImage cv2图片
    :return: bytesImage 二进制图片数据
    """
    return np.array(cv2.imencode('.png', image)[1]).tobytes()


def image_to_base64(image_np: bytes) -> str:
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


if __name__ == '__main__':
    filename = 'test.png'
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    print(type(img))
    print(img)
    image_code = image_to_base64(img)
    # print(image_code)

    img = base64_to_image(image_code)
    cv2.imshow('bytes2cv', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
