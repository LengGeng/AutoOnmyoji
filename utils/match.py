# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2019/9/25 14:26
# 文件名称  :   match.PY
# 开发工具  :   PyCharm
import cv2
from numpy import where, fromfile, uint8


class Match:
    # threshold = 0.9  # 图像识别相似度
    # match_res = False  # 匹配结果集
    image_path = 'images'  # 模板图片路径
    images = dict()  # 模板图片集

    def get_img(self, filename):
        """
        返回图片池中的该图片,若不存在则添加至图片池再返回
        :param filename: 图片文件名
        :return: 图片对象
        """
        if filename not in self.images:
            self.images[filename] = cv2.imread(self.image_path + '/' + filename)
        return self.images[filename]

    @staticmethod
    def cv_imread(filePath):
        return cv2.imdecode(fromfile(filePath, dtype=uint8), -1)

    @staticmethod
    def show_img(image, title='Image', time=0):
        """
        显示图片,按下任意键关闭
        :param image: 图片对象
        :param title: 标题
        :param time: 持续时间
        :return:
        """
        cv2.imshow(title, image)
        cv2.waitKey(time)
        cv2.destroyAllWindows()

    @staticmethod
    def match(image, target, threshold=0.95):
        """
        匹配 target 是否在 image 中
        :param image: 模板(大)
        :param target: 目标(小)
        :param threshold: 精确度
        :return: 匹配结果 boolean
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
        if res.max() >= threshold:
            return True
        return False

    @staticmethod
    def match_img(image, target, threshold):
        """
        从图片(image)中匹配,并标记匹配到的位置
        :param image: 模板(大)
        :param target: 目标(小)
        :param threshold: 精确度
        :return:
        """
        # 读入原图和模板
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        w, h = target.shape[::-1]
        # 标准相关模板匹配
        res = cv2.matchTemplate(img_gray, target, cv2.TM_CCOEFF_NORMED)
        loc = where(res >= threshold)  # 匹配程度大于value的坐标y,x
        show_img = image.copy()
        for pt in zip(*loc[::-1]):  # *号表示可选参数
            cv2.rectangle(show_img, pt, (pt[0] + w, pt[1] + h), (7, 249, 151), 2)
        cv2.imwrite('image_match.jpg', show_img)
        cv2.imshow('Detected', show_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def get_match_pos(image, target, threshold=0.95):
        """
        返回 target 在 image 中的所有坐标范围
        :param image: 模板(大)
        :param target: 目标(小)
        :param threshold: 精确度
        :return: 坐标列表
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        w, h = target.shape[::-1]
        res = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
        if res.max() >= threshold:
            loc = where(res >= threshold)  # 匹配程度大于value的坐标y,x
            pos_list = []
            for pt in zip(*loc[::-1]):  # *号表示可选参数
                if pos_list:
                    for p in pos_list:
                        if abs(pt[0] - p[0][0]) <= 5 and abs(pt[1] - p[0][1]) <= 5:
                            break
                    else:
                        pos_list.append([pt, (pt[0] + w, pt[1] + h)])
                else:
                    pos_list.append([pt, (pt[0] + w, pt[1] + h)])
            return pos_list
        else:
            return False

    @staticmethod
    def get_ratio_pos(image, *slices):
        """
        返回指定分辨率或图片大小的比例坐标点
        :param image: 图片对象或分辨率(string'111x222')
        :param slices: 比例坐标
        :return: 坐标列表
        """
        if type(image) == str:
            w, h = image.split('x')
            w, h = int(w), int(h)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            w, h = image.shape[::-1]
        if slices is None:
            return w, h
        pos_list = list()
        for pos in slices:
            x = w / pos[0] if pos[0] > 1 else w * pos[0]
            y = h / pos[1] if pos[1] > 1 else h * pos[1]
            pos_list.append((x, y))
        return pos_list

    @staticmethod
    def get_range_ratio_pos(begin, end, *slices):
        """
        返回指定范围内的比例坐标点
        :param begin: 范围开始点
        :param end: 范围结束点
        :param slices: 比例坐标点
        :return: 坐标列表
        """
        w, h = end[0] - begin[0], end[1] - begin[1]
        pos_list = []
        for pos in slices:
            x = w / pos[0] if pos[0] > 1 else w * pos[0]
            y = h / pos[1] if pos[1] > 1 else h * pos[1]
            pos_list.append((begin[0] + x, begin[1] + y))
        return pos_list


def _test():
    match = Match()

    target = match.get_img('end.jpg')
    print('测试图片池是否存储使用过的图片')
    target_next = match.get_img('end.jpg')
    template = match.get_img('jiangli.png')

    # print('多次匹配降低精确度问题')
    # for i in range(0, 5):
    #     match.match_img(target, template, 0.95)
    #     """
    #     使用cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (7, 249, 151), 2)会莫名造成后续匹配的精度降低
    #     使用下列代码可以有效解决问题
    #     show_img = image.copy
    #     cv2.rectangle(show_img, pt, (pt[0] + w, pt[1] + h), (7, 249, 151), 2)
    #     """

    print('测试match_img(图片匹配)')
    match.match_img(target, template, 0.95)

    print('测试match(是否检测到图像)')
    print(match.match(target, template, 0.95))

    print('测试get_match_pos(返回匹配坐标范围)')
    w, h = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY).shape[::-1]
    print(match.get_match_pos(target, template, 0.95))
    pos = match.get_match_pos(target, template, 0.95)[0][0]
    image = cv2.rectangle(target, pos, (pos[0] + w, pos[1] + h), (7, 249, 151), 2)
    match.show_img(image)

    # 测试图片/分辨率返回比例坐标点
    print(match.get_ratio_pos(target, (0.5, 0.2), (0.4, 0.8)))
    # 测试范围返回比例坐标点
    print(match.get_range_ratio_pos((100, 200), (500, 600), (0.5, 0.2), (0.4, 0.8)))


_match = Match()
show_img = _match.show_img
match = _match.match
cv_imread = _match.cv_imread
match_img = _match.match_img
get_match_pos = _match.get_match_pos
get_ratio_pos = _match.get_ratio_pos
get_range_ratio_pos = _match.get_range_ratio_pos

if __name__ == '__main__':
    _test()
