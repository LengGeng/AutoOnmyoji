from typing import Optional, List, Tuple

import cv2
import numpy as np

from utils.PosUtils import TupleScope, TuplePos, pos_distance
from utils.ImageUtils import CvImage, image_size, show, save_image, show_adapt


def match(image: CvImage, target: CvImage, accuracy: float = 0.95) -> bool:
    """
    匹配 target 是否在 image 中
    :param image: 模板(大)
    :param target: 目标(小)
    :param accuracy: 精确度
    :return: 匹配结果 boolean
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
    return result.max() >= accuracy


def find(image: CvImage, target: CvImage, accuracy: float = 0.95) -> Optional[TupleScope]:
    """
    匹配 target 在 image 中最可能的位置
    :param image: 模板(大)
    :param target: 目标(小)
    :param accuracy: 精确度
    :return: 匹配坐标
    :return:
    """
    # 灰度处理
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    # 执行匹配
    result = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
    # 最差匹配度,最优匹配度,最差匹配位置,最优匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    max_loc: TuplePos
    if max_val >= accuracy:
        w, h = image_size(target)
        return max_loc, (max_loc[0] + w, max_loc[1] + h)


def find_all(image, target, accuracy=0.95, gap: float = 0) -> List[TupleScope]:
    """
    匹配 target 在 image 中的所有坐标范围
    :param image: 模板(大)
    :param target: 目标(小)
    :param accuracy: 精确度
    :param gap: 间隔, 对间隔小于等于该值的点进行去重
    :return: 坐标列表
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
    location = np.where(result >= accuracy)  # 精确度大于value的坐标y,x

    pos_list = []
    w, h = image_size(target)
    for pt in zip(*location[::-1]):  # type: TuplePos
        # 去除邻近重复点
        for p in pos_list:
            # 排除距离过小的点
            if pos_distance(pt, p[0]) <= gap:
                break
        else:
            pos_list.append((pt, (pt[0] + w, pt[1] + h)))
    return pos_list


def find_knn(image: CvImage, target: CvImage, *, output: str = None, is_show: bool = False,
             MIN_MATCH_COUNT: int = 10) -> Optional[TupleScope]:
    """
    基于FLANN的匹配器(FLANN based Matcher)定位图片
    :param image: 模板(大)
    :param target: 目标(小)
    :param output: 保存标注的的图片路径, None为不保存
    :param is_show: 是否展示标注图片
    :param MIN_MATCH_COUNT: 最低特征点匹配数量
    :return: 坐标范围
    """
    # 创建sift检测器
    sift = cv2.SIFT_create()
    # find the key points and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(target, None)
    kp2, des2 = sift.detectAndCompute(image, None)
    # 设置Flann的参数
    FLANN_INDEX_KD_TREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KD_TREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    # 舍弃大于0.7的匹配结果
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    scope: Optional[TupleScope] = None
    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # 计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        w, h = image_size(target)
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        # 绘制目标区域范围
        image = image.copy()
        xy_axis = np.int32(dst)
        cv2.polylines(image, [xy_axis], True, 0, 2, cv2.LINE_AA)
        # 计算矩形范围
        x_axis: np.ndarray = xy_axis[:, :, [0]].flatten()
        y_axis: np.ndarray = xy_axis[:, :, [1]].flatten()
        scope = ((x_axis.min(), y_axis.min()), (x_axis.max(), y_axis.max()))
    else:
        print(f"Not enough matches are found - {len(good)}/{MIN_MATCH_COUNT}")
        matchesMask = None
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=(255, 0, 0),
                       matchesMask=matchesMask,
                       flags=2)  # 给特征点和匹配的线定义颜色
    mark_image = cv2.drawMatches(target, kp1, image, kp2, good, None, **draw_params)
    # 保存图片
    if output is not None:
        save_image(mark_image, output)
    # 展示结果
    if is_show:
        show(mark_image)
    # 返回结果
    return scope


def find_color(image: CvImage, color: Tuple[int, int, int], tolerance: int = 0) -> Optional[TuplePos]:
    """
    寻找颜色所在位置
    :param image: 模板(大)
    :param color: (r,g,b) 寻找的颜色
    :param tolerance: 容差值
    :return:
    """
    width, height = image_size(image)
    r1, g1, b1 = color[:3]
    for x in range(width):
        for y in range(height):
            pixel = image[y][x]
            # CvImage 是 b,g,r 模式
            b2, g2, r2 = pixel[:3]
            if abs(r1 - r2) <= tolerance and abs(g1 - g2) <= tolerance and abs(b1 - b2) <= tolerance:
                return x + 1, y + 1


def find_color_all(image: CvImage, color: Tuple[int, int, int], tolerance: int = 0) -> List[TuplePos]:
    """
    寻找颜色相同的所有位置
    :param image: 模板(大)
    :param color: (r,g,b) 寻找的颜色
    :param tolerance: 容差值
    :return:
    """
    poss = []
    width, height = image_size(image)
    r1, g1, b1 = color[:3]
    for x in range(width):
        for y in range(height):
            pixel = image[y][x]
            # CvImage 是 b,g,r 模式
            b2, g2, r2 = pixel[:3]
            if abs(r1 - r2) <= tolerance and abs(g1 - g2) <= tolerance and abs(b1 - b2) <= tolerance:
                poss.append((x + 1, y + 1))
    return poss


def find_multi_color(image: CvImage, color: Tuple[int, int, int],
                     offset_color_list: List[Tuple[int, int, Tuple[int, int, int]]],
                     tolerance: int = 0, offset_tolerance: int = None):
    """
    多点区域找色
    :param image: 目标图片
    :param color: 目标颜色
    :param offset_color_list: 目标颜色偏移位置对应的颜色 (offset_x,offset_y,color)
    :param tolerance: 目标颜色的容差值
    :param offset_tolerance: 偏移位置颜色的容差值
    :return:
    """
    if offset_tolerance is None:
        offset_tolerance = tolerance
    # 获取符合目标颜色的所有位置
    poss = find_color_all(image, color, tolerance)
    # TODO 过滤邻近的点
    # 依次检测每个点的偏移位置颜色是否符合
    for pos in poss:
        # 遍历所有偏移位置
        for offset_color in offset_color_list:
            offset_x, offset_y, offset_color = offset_color
            # 获取偏移位置的颜色
            x = pos[0] - 1 + offset_x
            y = pos[1] - 1 + offset_y
            # 位置错误,忽略该位置
            try:
                pos_color = image[y][x]
            except IndexError:
                continue
            b, g, r = pos_color[:3]
            r1, g1, b1 = offset_color
            # 对比颜色是否相同,不相同则退出
            if abs(r1 - r) > offset_tolerance or abs(g1 - g) > offset_tolerance or abs(b1 - b) > offset_tolerance:
                break
        else:  # 若循环中无退出则表示所有偏移位置均符合,返回该位置
            return pos


def check_color(image: CvImage, pos: TuplePos, color: Tuple[int, int, int], tolerance: int = 0) -> bool:
    """
    对比图片某一位置的颜色
    :param image: 图片
    :param pos: 位置
    :param color: 颜色
    :param tolerance: 容差值
    :return:
    """
    x, y = pos
    r1, g1, b1 = color[:3]
    # CvImage 是 b,g,r 模式
    b2, g2, r2 = image[y - 1][x - 1][:3]  # 像素位置 - 1 = 索引位置
    return abs(r1 - r2) <= tolerance and abs(g1 - g2) <= tolerance and abs(b1 - b2) <= tolerance


def mark(image: CvImage, scopes: List[TupleScope], color: Tuple[int, int, int] = (7, 249, 151),
         weight: int = 2):
    """
    对图片中的标记范围进行标记
    :param image: 图片
    :param scopes: 范围列表
    :param color: 颜色
    :param weight: 线宽
    :return:
    """

    mark_img = image.copy()
    for scope in scopes:
        cv2.rectangle(mark_img, scope[0], scope[1], color, weight)
    return mark_img


def match_mark(image: CvImage, target: CvImage, accuracy: float = 0.95,
               output: str = None, is_show: bool = True, adaptive: bool = True):
    """
    在 image 中标记 target
    :param image: 模板(大)
    :param target: 目标(小)
    :param accuracy: 精确度
    :param output: 保存标注的的图片路径, None为不保存
    :param is_show: 是否展示标注图片
    :param adaptive: 是否自适应显示
    :return:
    """
    # 匹配查找
    scope = find(image, target, accuracy)
    # 标记结果
    mark_image = mark(image, [scope]) if scope else image
    # 保存图片
    if output is not None:
        save_image(mark_image, output)
    # 展示结果
    if is_show:
        if adaptive:
            show_adapt(mark_image)
        else:
            show(mark_image)


def match_marks(image: CvImage, target: CvImage, accuracy: float = 0.95,
                output: str = None, is_show: bool = True, adaptive: bool = True):
    """
    在 image 中标记所有 target
    :param image: 模板(大)
    :param target: 目标(小)
    :param accuracy: 精确度
    :param output: 保存标注的的图片路径, None为不保存
    :param is_show: 是否展示标注图片
    :param adaptive: 是否自适应显示
    :return:
    """
    # 匹配查找
    scopes = find_all(image, target, accuracy)
    # 标记结果
    mark_image = mark(image, scopes)
    # 保存图片
    if output is not None:
        save_image(mark_image, output)
    # 展示结果
    if is_show:
        if adaptive:
            show_adapt(mark_image)
        else:
            show(mark_image)


def match_mark_bfm(image: CvImage, target: CvImage, *,
                   output: str = None, is_show: bool = True, adaptive: bool = True) -> None:
    """
    BFMatching
    :param image: 模板(大)
    :param target: 目标(小)
    :param output: 保存标注的的图片路径, None为不保存
    :param is_show: 是否展示标注图片
    :param adaptive: 是否自适应显示
    :return:
    """
    # 建立orb特征检测器
    orb = cv2.ORB_create()
    # 计算特征点和描述符
    kp1, des1 = orb.detectAndCompute(target, None)
    kp2, des2 = orb.detectAndCompute(image, None)
    # 建立匹配关系
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)  # 匹配描述符
    matches = sorted(matches, key=lambda x: x.distance)  # 据距离来排序
    # 绘制匹配关系
    mark_image = cv2.drawMatches(target, kp1, image, kp2, matches[:40], None, flags=2)
    # 保存图片
    if output is not None:
        save_image(mark_image, output)
    # 展示结果
    if is_show:
        if adaptive:
            show_adapt(mark_image)
        else:
            show(mark_image)


def match_mark_knn(image: CvImage, target: CvImage, *,
                   output: str = None, is_show: bool = True, adaptive: bool = True) -> None:
    """
    基于FLANN的匹配器(FLANN based Matcher)
    :param image: 模板(大)
    :param target: 目标(小)
    :param output: 保存标注的的图片路径, None为不保存
    :param is_show: 是否展示标注图片
    :param adaptive: 是否自适应显示
    :return:
    """
    # 创建sift检测器
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(target, None)
    kp2, des2 = sift.detectAndCompute(image, None)
    # 设置Flann的参数
    FLANN_INDEX_KD_TREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KD_TREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # 设置好初始匹配值
    matchesMask = [[0, 0] for _ in range(len(matches))]
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.5 * n.distance:  # 舍弃小于0.5的匹配结果
            matchesMask[i] = [1, 0]
    drawParams = dict(matchColor=(0, 0, 255), singlePointColor=(255, 0, 0), matchesMask=matchesMask,
                      flags=0)  # 给特征点和匹配的线定义颜色
    mark_image = cv2.drawMatchesKnn(target, kp1, image, kp2, matches, None, **drawParams)  # 画出匹配的结果
    # 保存图片
    if output is not None:
        save_image(mark_image, output)
    # 展示结果
    if is_show:
        if adaptive:
            show_adapt(mark_image)
        else:
            show(mark_image)
