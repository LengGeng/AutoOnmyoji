# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2019/9/26 16:21
# 文件名称  :   onmyoji.PY
# 开发工具  :   PyCharm
import os
import time
from utils.match import *
from utils.adb import Adb
from utils import functions as fun
from stopit import threading_timeoutable
from utils.logger import get_logger
from stopit.utils import TimeoutException


class Onmyoji:
    threshold = 0.8  # 图像识别相似度
    image_path = "images"  # 模板图片路径
    images = dict()  # 模板图片集

    def __init__(self):
        self.adb = Adb()
        self.module = ""

    # 获取图片对象
    def get_img(self, filename):
        """
        返回图片池中的该图片,若不存在则添加至图片池再返回
        :param filename: 图片文件名
        :return: 图片对象
        """
        if filename not in self.images:
            # self.images[filename] = cv2.imread(self.image_path + "/" + filename)
            self.images[filename] = cv_imread(os.path.join(self.image_path, filename))
        return self.images[filename]

    # 返回模块的文件路径
    def get_module_path(self, filename, module=None):
        """
        返回模块的文件路径
        :param filename: 文件名
        :param module: 模块
        :return: 路径
        """
        if module:
            return os.path.join(module, filename)
        else:
            return os.path.join(self.module, filename)
        pass

    # 匹配图像
    def match(self, template, module=None):
        """
        当前设备图片识别
        :param template: 识别图片对象或路径
        :param module: 当template为路径时,可以指定的模块路径
        :return: 匹配结果 boolean
        """
        if type(template) == str:
            template = self.get_img(self.get_module_path(template, module))
        return match(self.adb.screen, template)

    def matchs(self, *args):
        """同时匹配多个图片
        self.match的加强版,同时匹配多个普片
        :param args: match函数的参数集合的列表 [(arg1,arg2...),...]
        :return: 多个匹配中是否有匹配到
        """
        return any(self.match(*arg) for arg in args)

    # 匹配图像坐标
    def match_touch(self, template, module=None):
        """
        匹配并点击图像在设备截图中的随机点
        :param template: 识别图片对象或路径
        :param module: 当template为路径时,可以指定的模块路径
        :return:
        """
        if type(template) == str:
            template = self.get_img(self.get_module_path(template, module))
        pos_list = get_match_pos(self.adb.screen, template, self.threshold)
        if pos_list:
            pos = fun.get_random_pos(*pos_list[0])
            if pos:
                self.adb.click(pos)
                return True
        return False

    # 挑战
    def combat(self, count):
        i = 0
        while i < count:
            if self.__combat__():
                i += 1
                self.logger.info("当前为第{}次挑战".format(i))
        self.logger.info("任务结束，总共进行了{}次挑战".format(i))

    # 业原火
    def yeyuanhuo(self, tan=0, zen=0, chi=0):
        self.module = "业原火"
        self.logger.info("任务: " + self.module)
        option = list("贪嗔痴")
        options = {"贪": int(tan), "嗔": int(zen), "痴": int(chi)}
        for category in option:
            self.logger.info("%s\t%s" % (category, options[category]))
        self.adb.screenshot()
        # 进入业原火界面
        for i in range(5):
            if self.match_touch("探索.png", "主页"):
                self.logger.info("进入探索页面")
                fun.random_time(4, 5)
                self.adb.screenshot()
                if self.match_touch("御魂.png", "公共"):
                    self.logger.info("进入御魂页面")
                    fun.random_time(1.5, 3)
                    pos = get_ratio_pos(self.adb.screen, [0.6, 0.3], [0.8, .75])
                    self.logger.info(pos)
                    self.adb.click(pos)
                    self.logger.info("进入业原火页面")
                    break
        # 检查是否锁定阵容
        self.__locking__()
        # 开始业原火流程
        for category in option:
            count = options[category]
            if count:
                if self.match_touch("%s.png" % category):
                    self.logger.info("切换至" + category)
                i = 0
                while i < count:
                    if self.__combat__():
                        i += 1
                        self.logger.info("当前为第%s次%s" % (i, category))
                self.logger.info("总共进行了%s次%s" % (i, category))

    # 组队
    def zudui(self, count):
        """
        组队司机功能
        :param count: 挑战次数
        :return:
        """
        self.module = "组队"
        self.logger.info("任务：组队司机")
        self.logger.info("目标：{}次".format(count))
        i = 0
        while i < int(count):
            self.adb.screenshot()
            if self.__locking__():
                if self.match("组队开始标志.png"):
                    if self.match_touch("挑战.png"):
                        self.logger.info("开始战斗")
                        self.__ready__(timeout=8)  # 准备
                        if self.__end__(invite=True):
                            i += 1
                            self.logger.info("当前已进行{}次".format(i))
                    else:
                        self.logger.warning("未匹配到开始战斗按钮")
                else:
                    self.logger.warning("暂未匹配到队友,等待...")
                continue
            else:
                self.logger.warning("未检查到组队界面")

    # 乘客
    def chengke(self, count: int, accept: bool = True):
        """
        组队乘客功能
        :param count: 挑战次数
        :param accept: 接受默认邀请
        :return:
        """
        self.logger.info("任务：组队乘客")
        self.logger.info("目标：{}次".format(count))
        i = 0
        while i < int(count):
            self.adb.screenshot()
            if accept:
                if self.__accept_invite__(timeout=8):
                    accept = False
            self.__ready__(timeout=5)
            if self.__end__():
                i += 1
                self.logger.info("当前已进行{}次".format(i))

    # 结界突破
    def jiejie(self):
        """
        结界突破功能
        :return:
        """
        self.module = "结界"
        self.logger.info("任务: 结界突破")
        # 结界对象大小
        jiejie_object_width = 455
        jiejie_object_height = 160
        while True:
            self.adb.screenshot()
            # 检查是否在结界界面
            if not (self.match("突破标志.png") or self.match("突破标志.png")):
                self.logger.warning("当前不在结界界面")
                if self.match_touch("结界突破.png", "公共"):
                    self.logger.info("已自动进入结界突破界面")
                    self.adb.screenshot()
                else:
                    self.logger.error("无法进入结界突破界面,任务停止")
                    break
            # 匹配目标
            screen = self.adb.screen
            self.adb.threshold = 0.98
            # 判断当前次数
            if self.match("寮次数.png"):
                self.logger.warning("突破次数不足")
                fun.random_time(1500, 2000)
            self.adb.threshold = 0.9
            self.logger.info("获取结界目标")
            pos_list = get_match_pos(self.adb.screen, self.get_img("突破对象标志.png"), 0.92)
            if pos_list:
                self.logger.info("获取到{}个结界目标".format(len(pos_list)))
                # 开始遍历结界目标
                for pos in pos_list:
                    self.adb.screenshot()
                    if not self.match_touch("宝箱.png", "公共"):
                        self.match_touch("宝箱2.png", "公共")
                    pos_begin = (pos[1][0] - jiejie_object_width, pos[1][1] - jiejie_object_height)
                    pos_end = pos[1]
                    self.logger.info("开始节点：{}结束节点：{}".format(pos_begin, pos_end))
                    # 判断坐标真实有效,排除显示不全的目标
                    if pos_begin[0] > 0 and pos_begin[1] > 0:
                        jiejie_img = screen[pos_begin[1]:pos_end[1], pos_begin[0]:pos_end[0]]
                        show_img(jiejie_img, time=800)
                        if match(jiejie_img, self.get_img(self.get_module_path("败北.png"))):
                            self.logger.info("目标状态：败北")
                        elif match(jiejie_img, self.get_img(self.get_module_path("击破.png"))):
                            self.logger.info("目标状态：击破")
                        else:
                            self.logger.info("目标状态：未突破")
                            self.adb.click(fun.get_random_pos(*pos))  # ####
                            fun.random_time(1.2, 1.8)
                            self.adb.screenshot()
                            if self.match_touch("进攻.png"):
                                self.logger.info("开始突破")
                                self.adb.screenshot()
                                if self.__box_end__():
                                    self.logger.info("突破成功")
                                    fun.random_time(2.5, 3)
                                    break
                                else:
                                    self.logger.info("突破失败")
                            else:
                                self.logger.info("未检测到结界挑战页面")
                    else:
                        self.logger.warning("无效的坐标")
                # 遍历完后滑动列表
                else:
                    self.adb.slide_event(1200, 875, dc="u", distance=700)
                    fun.random_time(0.5, 1)
            else:
                self.logger.warning("未获取到结界目标")

    # 万事屋
    def wanshiwu(self):
        self.module = "万事屋/"
        # 进入万事屋
        self.adb.screenshot()
        self.logger.info("尝试进入万事屋")
        self.match_touch("进入万事屋.png")
        fun.random_time(3, 5)
        self.adb.screenshot()
        self.logger.info("尝试进入事件")
        self.match_touch("进入事件.png")
        fun.random_time(2, 3.5)
        # 自动领取奖励主循环
        while True:
            self.adb.screenshot()
            # 异常检查
            self.__check__()
            # 检测突发状况Buff
            if self.match("事件_突发状况.png"):
                self.logger.info("检测到突发状况Buff")
                self.match_touch(fun.choice(["事件_一键领取.png"]))
            # 检测未关闭的奖励页面
            if self.match("事件_奖励.png"):
                self.match_touch(fun.choice(["事件_一键领取.png"]))
            # 领取循环
            fun.random_time(3, 5)
            self.adb.screenshot()
            if self.match_touch("事件_一键领取.png"):
                self.logger.info("一键领取奖励")
                start = time.time()
                while True:
                    fun.random_time(2, 5)
                    self.adb.screenshot()
                    if self.match("事件_奖励.png"):
                        self.match_touch(fun.choice(["事件_一键领取.png"]))
                        self.logger.info("成功领取奖励")
                        # 检测无法自动领取的奖励
                        # pass
                        self.logger.info("进入等待")
                        break
                    if time.time() - start > 15:
                        self.logger.warning("点击了一键领取奖励，但未检测到奖励页面。")
                        break
                fun.random_time(60 * 5, 60 * 10)
            else:
                self.logger.error("不在程序运行所需场景，请切换至{万事屋=>事件}场景。")

    # 超鬼王
    def chaoguiwang(self):
        """
        超鬼王功能
        :return:
        """
        self.module = "超鬼王"
        rouse_count = 0
        count = 0
        kyLin = ["火麒麟.png", "风麒麟.png", "水麒麟.png", "雷麒麟.png"]
        self.logger.info("任务: 超鬼王")
        while count < 100:
            self.adb.screenshot()  # 截图
            self.match_touch("觉醒.png", "公共")  # 匹配点击图片
            fun.random_time(1, 1.8)  # 随机等待
            self.adb.screenshot()  # 截图
            self.match_touch(fun.choice(kyLin))  # 选择列表中随机一个进行点击
            if self.__locking__():
                self.logger.info("当前阵容已处于锁定状态")

                # 进入循环挑战觉醒阶段
                self.logger.info("进入循环挑战觉醒阶段")
                while True:
                    fun.random_time(0.8, 1.3)  # 随机等待
                    self.adb.screenshot()  # 截图
                    if self.match_touch("发现超鬼王.png"):
                        self.match_touch("发现超鬼王.png")
                        self.logger.info("发现超鬼王")
                        break  # 跳出觉醒循环
                    if self.match_touch("挑战.png", "觉醒"):
                        self.logger.info("开始挑战")
                        # 等待挑战结束
                        if self.__end__():
                            rouse_count += 1
                            self.logger.info("当前已进行%s次觉醒" % rouse_count)

                # 进入超鬼王阶段
                self.logger.info("进入超鬼王阶段")
                while True:
                    fun.random_time(1.3, 1.8)  # 随机等待
                    self.adb.screenshot()  # 截图
                    while True:
                        fun.random_time(0.8, 1.3)  # 随机等待
                        self.adb.screenshot()  # 截图
                        if not self.match_touch("挑战.png"):
                            break
                        self.logger.info("开始挑战超鬼王")
                        # 准备
                        self.__ready__()
                        # 等待结束
                        if self.__end__():
                            count += 1
                    if self.match_touch("返回.png", "公共"):
                        self.logger.info("击败超鬼王,跳出超鬼王阶段")
                        self.logger.info("当前已击败%s只鬼王" % count)
                        break

    # 初始化Logger
    def __init_logger__(self):
        LOG_DIR_NAME = os.path.join("log", self.adb.device.strip().split(" ")[-1])
        if not os.path.exists(LOG_DIR_NAME):
            os.makedirs(LOG_DIR_NAME)
        LOG_FILENAME = os.path.join(LOG_DIR_NAME, time.strftime("LOG_%Y%m%d.log", time.localtime()))
        self.logger = get_logger(LOG_FILENAME)
        self.logger.info("*" * 15 + "启动" + "*" * 15)

    # 宝箱结束
    def __box_end__(self, invite=False):
        """
        判断并点击界面跳过结算界面(旧版本宝箱结算)
        :return: 结算结果
        """
        # 等待结束
        while True:
            end_sign = None  # 结算成功标志
            self.adb.screenshot()  # 截图
            # 一旦检测到结算标志进入循环,再次检测不到退出
            while self.matchs(
                    ("贪吃鬼.png", "公共"),
                    ("宝箱2.png", "公共"),
                    ("宝箱.png", "公共"),
                    ("战斗胜利.png", "公共"),
                    ("战斗失败.png", "公共")):
                self.logger.info("检测到结算页面")
                end_sign = True
                # 默认邀请队友
                if invite:
                    if self.__invite__():
                        break
                if self.match("战斗失败.png", "公共"):
                    self.logger.info("检测到战斗失败")
                    end_sign = False
                end_regions = [
                    [[0.625, 0.9], [0.8, 0.98]],
                    [[0.93, 0.33], [0.98, 0.66]],
                ]
                pos = fun.get_random_pos(*get_ratio_pos(self.adb.screen, *fun.choice(end_regions)))
                self.logger.info(f"点击屏幕:{pos}")
                self.adb.click(pos)
                fun.random_time(2, 2.5)  # 随机等待
                self.adb.screenshot()  # 截图
            fun.random_time(0.5, 0.8)  # 随机等待
            if end_sign is not None:  # 结算后跳出结算循环
                self.logger.info("结算成功")
                return end_sign

    # 结束
    def __end__(self, invite=False):
        """
        判断并点击界面跳过结算界面
        :return: 结算结果
        """
        # 等待结束
        while True:
            end_sign = None  # 结算成功标志
            self.adb.screenshot()  # 截图
            # 一旦检测到结算标志进入循环,再次检测不到退出
            while self.match("结束标志.png", "公共") or self.match("战斗胜利.png", "公共") or self.match("战斗失败.png", "公共"):
                end_sign = True
                # 默认邀请队友
                if invite:
                    if self.__invite__():
                        break
                if self.match("战斗失败.png", "公共"):
                    end_sign = False
                end_regions = [
                    [[0.625, 0.9], [0.8, 0.98]],
                    [[0.93, 0.33], [0.98, 0.66]],
                ]
                pos = fun.get_random_pos(*get_ratio_pos(self.adb.screen, *fun.choice(end_regions)))
                self.adb.click(pos)
                fun.random_time(0.5, 0.8)  # 随机等待
                self.adb.screenshot()  # 截图
            fun.random_time(0.8, 1)  # 随机等待
            if end_sign is not None:  # 结算后跳出结算循环
                self.logger.info("结算成功")
                return end_sign

    # 准备
    @threading_timeoutable()
    def __ready__(self):
        """
        准备
        :param timeout: 超时时间
        :return: 是否成功准备
        """
        try:
            ready_sign = False
            while True:
                self.adb.screenshot()  # 截图
                while self.match("准备.png", "公共"):
                    self.adb.screenshot()  # 截图
                    self.match_touch("准备.png", "公共")
                    ready_sign = True
                if ready_sign:
                    self.logger.info("准备")
                    return True
        except TimeoutException:
            self.logger.warning("准备超时退出")

    # 开启默认邀请
    def __invite__(self):
        """
        开启默认邀请
        :return: 是否开启默认邀请成功
        """
        if self.match_touch("默认邀请.png", "组队"):
            fun.random_time(0.2, 0.5)
            if self.match_touch("确定.png", "公共"):
                self.logger.info("开启默认邀请")
                return True
            else:
                self.logger.warning("默认邀请失败")
                return False

    # 开启接受默认邀请
    @threading_timeoutable()
    def __accept_invite__(self):
        try:
            while True:
                if self.match_touch("同意默认邀请.png", "组队"):
                    self.logger.info("同意接受默认邀请")
                    return True
        except TimeoutException:
            self.logger.warning("没有收到队友的默认邀请")

    # 正常挑战
    def __combat__(self):
        """
        正常挑战,循环点击挑战与结束
        :return:
        """
        self.adb.screenshot()
        if self.match_touch("挑战_业原火.png", "业原火") or self.match_touch("挑战_菱形.png", "公共"):
            self.logger.info("开始挑战")
            self.__ready__(timeout=8)
            if self.__box_end__():
                self.logger.info("结束挑战")
                return True
        return False

    # 异常检测
    def __check__(self):
        """
        检测异常行为,如悬赏任务等
        :return:
        """
        self.logger.warning("开始执行异常检测")
        self.__reward_task__()

    # 协作邀请
    def __reward_task__(self, accept=False):
        category_dir = "异常处理/"
        if self.match(category_dir + "协作邀请.png"):
            self.logger.info("检测到协作邀请")
            if accept:
                self.match_touch("公共/" + "同意.png")
                self.logger.info("协作邀请已同意")
            else:
                self.match_touch("公共/" + "拒绝.png")
                self.logger.info("协作邀请已拒绝")

    # 确认阵容锁定状态
    def __locking__(self):
        """
        确认阵容锁定状态
        :return: bool
        """
        if self.match("锁.png", "公共"):
            self.logger.info("当前阵容已处于锁定状态")
            return True
        elif self.match_touch("锁_开.png", "公共"):
            self.logger.info("当前阵容未锁定,已为您自动锁定")
            return True
        else:
            self.logger.info("未检测到阵容锁定按钮")
            return False

    # 测试
    def test(self):
        self.logger.info("测试函数开始执行")
        for _ in range(10):
            self.logger.info("测试函数执行")
            fun.random_time(1, 2)
        self.logger.info("测试函数执行结束")


def _test():
    onmyoji = Onmyoji()
    onmyoji.adb.connect_device()
    onmyoji.__init_logger__()
    # onmyoji.zudui(1234)
    onmyoji.combat(500)
    # onmyoji.yeyuanhuo(12, 34, 56)
    # onmyoji.jiejie()


if __name__ == '__main__':
    _test()
