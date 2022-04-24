from typing import Optional, List, Tuple

import cv2
import numpy as np

from drive import Scope
from utils.imageUtils import CvImage, save_image, image_size, show_adapt


def match_in(image: CvImage, template: CvImage, threshold: float = 0.95) -> bool:
    """
    匹配 template 是否在 image 中
    :param image: 匹配图像(大)
    :param template: 匹配目标(小)
    :param threshold: 精确度
    :return: 匹配结果
    """
    image_gary = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gary = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(image_gary, template_gary, cv2.TM_CCOEFF_NORMED)
    return res.max() >= threshold


# ref: https://blog.csdn.net/zhuisui_woxin/article/details/84400439
# 模板匹配方式
#     cv2.TM_SQDIFF、cv2.TM_SQDIFF_NORMED
#         匹配度越趋近于0越好, 故取min值
#     其它
#         匹配度越趋近与1越好, 故取max值
def _match_template(
        image: CvImage, template: CvImage, method: int = cv2.TM_CCOEFF_NORMED, mask: Optional[CvImage] = None
) -> Tuple[float, Tuple[int, int]]:
    """
    单目标匹模板配
    :param image: 搜索的图像(大)
    :param template: 搜索的模板(小)
    :param method: 匹配模式 cv2.matchTemplate 的 method 参数
    :param mask: 模板遮罩
    :return: 坐标范围
    """
    # 灰度处理
    image_gary = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gary = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # 执行匹配
    result: np.ndarray = cv2.matchTemplate(image_gary, template_gary, method, mask)
    # 最差匹配度,最优匹配度,最差匹配位置,最优匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 获取不同匹配模式下的匹配度及位置
    if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
        val = 1 - min_val
        loc = min_loc
    else:
        val = max_val
        loc = max_loc
    # print(f"min_val={min_val}")
    # print(f"min_loc={min_loc}")
    # print(f"max_val={max_val}")
    # print(f"max_loc={max_loc}")
    # print(f"val={val}")
    # print(f"loc={loc}")
    return val, loc


def _match_templates(
        image: CvImage, template: CvImage, threshold: float = 0.95,
        method: int = cv2.TM_CCOEFF_NORMED, mask: Optional[CvImage] = None
) -> np.ndarray:
    """
    多目标匹模板配
    :param image: 搜索的图像(大)
    :param template: 搜索的模板(小)
    :param threshold: 匹配度[0,1]
    :param method: 匹配模式 cv2.matchTemplate 的 method 参数
    :param mask: 模板遮罩
    :return: 坐标范围
    """
    # 执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(image, template, method, mask)
    # 筛选满足匹配度的坐标
    if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
        locs = np.where(result <= 1 - threshold)
    else:
        locs = np.where(result >= threshold)
    return locs


def match_template(
        image: CvImage, template: CvImage, threshold: float = 0.95,
        method: int = cv2.TM_CCOEFF_NORMED, mask: Optional[CvImage] = None
) -> Optional[Scope]:
    """
    匹配 template 在 image 中的位置
    :param image: 搜索的图像(大)
    :param template: 搜索的模板(小)
    :param threshold: 匹配度[0,1]
    :param method: 匹配模式 cv2.matchTemplate 的 method 参数
    :param mask: 模板遮罩
    :return: 坐标范围
    """
    # 匹配所在位置
    val, loc = _match_template(image, template, method, mask)
    if val >= threshold:
        w, h = image_size(template)
        return Scope(loc, (loc[0] + w, loc[1] + h))


def match_templates(
        image: CvImage, template: CvImage, threshold: float = 0.95,
        method: int = cv2.TM_CCOEFF_NORMED, mask: Optional[CvImage] = None
) -> List[Scope]:
    """
    匹配 template 在 image 中的所有位置
    :param image: 搜索的图像(大)
    :param template: 搜索的模板(小)
    :param threshold: 匹配度[0,1]
    :param method: 匹配模式 cv2.matchTemplate 的 method 参数
    :param mask: 模板遮罩
    """
    locs = _match_templates(image, template, threshold, method, mask)
    scope_list: List[Scope] = []
    if locs:
        # 获得模板图片的高宽尺寸
        w, h = image_size(template)
        # 遍历提取出来的位置
        loc: Tuple[int, int]
        for loc in zip(*locs[::-1]):
            if scope_list:
                # 筛选x或y轴偏移大于5个像素的结果,locs中的坐标是从小到大的,因此后面的总是>=前面的
                if (loc[0] - scope_list[-1].s.x > 5) or (loc[1] - scope_list[-1].s.y > 5):
                    scope_list.append(Scope(loc, (loc[0] + w, loc[1] + h)))
            else:
                scope_list.append(Scope(loc, (loc[0] + w, loc[1] + h)))

    return scope_list


def match_mark(
        image: CvImage, template: CvImage, threshold: float = 0.95, filename: Optional[str] = None,
        method: int = cv2.TM_CCOEFF_NORMED, mask: Optional[CvImage] = None
) -> None:
    """
    匹配 template 在 image 的位置,并标记
    :param image: 搜索的图像(大)
    :param template: 搜索的模板(小)
    :param threshold: 匹配度[0,1],大于精确度的使用绿色标记,小于精确度的使用红色标记
    :param filename: 标记图片保存位置，None为不保存
    :param method: 匹配模式 cv2.matchTemplate 的 method 参数
    :param mask: 模板遮罩
    :return:
    """
    # 匹配所在位置
    val, loc = _match_template(image, template, method, mask)
    # 复制图片进行标记
    match_image = image.copy()
    # 获取图片模板大小
    w, h = image_size(template)
    # 判断匹配度是否符合
    MARK_COLOR = (0, 255, 0) if val >= threshold else (0, 0, 255)
    # 绘制矩形边框，将匹配区域标注出来
    cv2.rectangle(match_image, loc, (loc[0] + w, loc[1] + h), MARK_COLOR, 2)
    # 保存图片
    if filename is not None:
        save_image(match_image, filename)
    # 展示图片
    show_adapt(match_image, "Match")


def match_marks(
        image: CvImage, template: CvImage, threshold: float = 0.95, filename: Optional[str] = None,
        method: int = cv2.TM_CCOEFF_NORMED, mask: Optional[CvImage] = None
) -> None:
    """
    匹配 template 在 image 的所有位置,并标记
    :param image: 搜索的图像(大)
    :param template: 搜索的模板(小)
    :param threshold: 匹配度[0,1],大于精确度的使用绿色标记,小于精确度的使用红色标记
    :param filename: 标记图片保存位置，None为不保存
    :param method: 匹配模式 cv2.matchTemplate 的 method 参数
    :param mask: 模板遮罩
    :return:
    """
    scopes = match_templates(image, template, threshold, method, mask)
    mark_image = image.copy()
    for scope in scopes:
        # 绘制矩形边框，将匹配区域标注出来
        cv2.rectangle(mark_image, scope.s.value, scope.e.value, (0, 255, 0), 2)
    # 保存图片
    if filename is not None:
        save_image(mark_image, filename)
    # 展示图片
    show_adapt(mark_image, "Match")


def _test():
    from utils.imageUtils import read_image
    target = read_image("../test/image/target.jpg")
    targets = read_image("../test/image/targets.jpg")
    template = read_image("../test/image/template.jpg")
    # 匹配是否在目标中
    print("匹配是否在目标中:", match_in(target, template, 0.95))
    # 单目标
    # 匹配并返回坐标
    print("匹配并返回坐标:", match_template(target, template, 0.95))
    # 匹配并标记
    match_mark(target, template, 0.95)
    # 多目标
    # 多目标匹配并返回坐标
    print("多目标匹配并返回坐标:", match_templates(targets, template, 0.95))
    # 多目标匹配并标记
    match_marks(targets, template, 0.95)


if __name__ == '__main__':
    _test()
