from pathlib import Path
from typing import Optional, Union, List

from utils.ImageUtils import CvImage, read_image

DEFAULT_ACCEPT_SUFFIX = [".png", ".jpg", ".jpeg", ".bmp"]


class Nothing:
    """
    Nothing 主要用于解决连续链式调用(a.b.c.d...)的中间报错,类似于 JavaScript 中的 a?.b?.c
    Nothing 是等于 None 的,但由于无法重写 is 的判定,一次需要使用 ==
    """

    def get(self, key):
        return self

    def __getattr__(self, item):
        return self

    def __getitem__(self, item):
        return self

    def __eq__(self, other):
        return other is None

    def __bool__(self):
        return False

    def __str__(self):
        return f"{self.__class__.__name__}()"


NOTHING = Nothing()


class ImagePool(object):
    def __init__(self, root_path: Union[Path, str], work_path: Union[Path, str] = None, images: dict = None,
                 strict: bool = False, scan: bool = False, ignore_suffix: bool = False,
                 cache_sub_pool: bool = True,
                 accept_suffix: Optional[List[str]] = None):
        """
        初始化一个图片池
        :param root_path: 根目录
        :param work_path: 工作目录
        :param images: 图片数据保存的字典
        :param strict: 是否启用严格模式(获取不存在的图片直接报错)
        :param scan: 是否自动工作目录(扫描目录下的图片文件)
        :param ignore_suffix: 是否忽略后缀(第一次时需要带后缀才可以正确读取文件,之后不需要带后缀)
        :param cache_sub_pool: 是否缓存子目录的图片池
        :param accept_suffix: 自动读取时扫描文件的后缀
        """
        # 保存参数
        self._kwargs = {
            "scan": scan,
            "strict": strict,
            "ignore_suffix": ignore_suffix,
            "cache_sub_pool": cache_sub_pool,
            "accept_suffix": accept_suffix,
        }
        self._strict = strict
        self._ignore_suffix = ignore_suffix
        self._cache_sub_pool = cache_sub_pool
        self._images = {} if images is None else images
        # 根目录
        self.root_path: Path = (root_path if isinstance(root_path, Path) else Path(root_path)).resolve()
        # 检查目录
        if not self.root_path.exists():
            raise FileNotFoundError("根目录不存在")
        # 工作目录
        if work_path is None:
            self.work_path: Path = self.root_path
        elif isinstance(work_path, Path):
            try:
                work_path = work_path.resolve()
                work_path.relative_to(self.root_path)
                self.work_path: Path = work_path
            except ValueError:
                raise ValueError("工作目录应该是根目录的子目录")
        else:
            self.work_path: Path = self.root_path.joinpath(work_path).resolve()
        # 检查工作目录
        if not self.work_path.exists():
            raise FileNotFoundError("工作目录不存在")
        # 允许的文件类型
        self.accept_suffix = accept_suffix or DEFAULT_ACCEPT_SUFFIX
        # 自动扫描目录下的图片文件
        if scan:
            self._scan_()

    def _scan_(self):
        """
        自动扫描读取目录下的图片文件
        :return:
        """
        for accept_suffix in self.accept_suffix:
            for filepath in self.work_path.glob(f"*{accept_suffix}"):
                key = self._get_key_(filepath)
                self._images[key] = read_image(str(filepath))

    def cwd(self) -> Path:
        """
        获取当前工作目录
        :return:
        """
        return self.work_path

    def home(self) -> Path:
        """
        获取根(家)目录
        :return:
        """
        return self.root_path

    @property
    def images(self):
        return self._images.keys()

    def _get_key_(self, filepath: Path) -> str:
        key = filepath.relative_to(self.root_path)
        if self._ignore_suffix:
            key = str(key).replace(key.name, key.stem)
        else:
            key = str(key)
        return key

    def get(self, path: str) -> Union[Nothing, CvImage, "ImagePool"]:
        if path is None:
            raise ValueError("图片路径不能是 `None`")
        filepath = self.work_path.joinpath(path)
        key = self._get_key_(filepath)
        # 判断是否存在
        if key in self._images:  # 存在直接返回
            return self._images[key]
        else:  # 不存在尝试读取
            if filepath.exists():
                # 为子目录
                if filepath.is_dir():
                    # 创建子目录图片池
                    pool = ImagePool(self.root_path, filepath, self._images, **self._kwargs)
                    if self._cache_sub_pool:
                        self._images[key] = pool
                    return pool
                else:
                    image = read_image(str(filepath))
                    self._images[key] = image
                    return image
            else:
                # 严格模式直接报错,非严格模式返回None
                if self._strict:
                    raise FileNotFoundError(f"Image file `{filepath}` not found")
                else:
                    return NOTHING

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        return self.get(item)

    def __str__(self):
        return f"{self.__class__.__name__}({self.work_path})"
