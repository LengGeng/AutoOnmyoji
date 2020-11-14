import os.path
from os import makedirs


def check_dirs(dirs, title=None):
    """检查目录
    检查目录是否存在,不存在则创建
    :param dirs: 目录
    :param title: 不存在时提示的目录说明
    :return:
    """
    if not (os.path.exists(dirs) and os.path.isdir(dirs)):
        if title:
            print(title, "\t目录不存在")
        makedirs(dirs)
        if title:
            print(title, "\t目录已创建")


def init_file(filepath: str, size: int):
    """文件初始化
    创建指定大小的文件,用于预下载
    :param filepath: 文件路径
    :param size: 文件大小(bytes)
    :return:
    """
    print("\r初始化文件中...", end="")
    with open(filepath, "wb") as f:
        f.seek(size - 1)
        f.write(bytes(1))
    print("\r文件初始化完成")


def size_format(size: int, *, pro: int = 1.0, dec: int = 2):
    """文件大小格式化
    :param size: 文件大小，单位byte
    :param pro: 单位转换进行的比例
    :param dec: 文件大小浮点数的精确单位
    :return: 文件单位格式化大小
    """
    unit: list = ["B", "KB", "MB", "GB", "TB", "PB"]
    pos: int = 0
    while size >= 1024 * pro:
        size /= 1024
        pos += 1
        if pos >= len(unit):
            break
    return str(round(size, dec)) + unit[pos]


def walk_open(path, *args, **kwargs):
    """迭代打开目录下的所有文件
    :param path: 起始目录
    :return: path,fp(文件路径,文件打开对象)
    """
    if os.path.isdir(path):
        for sub_path in os.listdir(path):
            sub_path = os.path.join(path, sub_path)
            for data in walk_open(sub_path, *args, **kwargs):
                yield data
    elif os.path.isfile(path):
        with open(path, *args, **kwargs) as fp:
            yield path, fp


def replace_invalid_filename_char(filename, replaced_char='_'):
    """
    Replace the invalid character in the filename with specified character.
    The default replaced character is '_'.
    e.g.
    C/C++ -> C_C++
    :param filename: filename
    :param replaced_char: replace with character
    :return: string
    """
    valid_filename = filename
    invalid_characters = '\\/:*?"<>|'
    for char in invalid_characters:
        valid_filename = valid_filename.replace(char, replaced_char)

    return valid_filename
