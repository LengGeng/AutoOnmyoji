# _*_ coding  :  UTF-8 _*_
# 开发团队  :   冷羹
# 开发人员  :   冷羹
# 开发时间  :   2019/9/26 16:21
# 文件名称  :   onmyoji.PY
# 开发工具  :   PyCharm
import random

import settings
from auto import Auto
from drives import MiniDriver, choose_driver, Driver
from utils.ImagePoolUtils import ImagePool
from utils.PosUtils import Scope, get_proportion_pos
from utils.match import Match
from utils import functions as fun, LogUtils
from stopit import threading_timeoutable

import os
import time


class BaseOnmyoji:
    threshold = 0.8  # 图像识别相似度
    images = ImagePool(settings.TEMPLATE_IMAGE_PATH)  # 模板图片集

    def __init__(self, driver: Driver):
        self.driver = driver
        self.auto = Auto(driver)
        self._init_log_()
        self._init_scope_()

    # 初始化Logger
    def _init_log_(self):
        log_path = os.path.join(self.driver.log_dir, "script.log")
        self.logger = LogUtils.LogUtils(__name__).add_file_handler(log_path, LogUtils.DEBUG).getLogger()
        self.logger.info("*" * 15 + "Script Start" + "*" * 15)

    def _init_scope_(self):
        self.screen_scope = Scope((0, 0), self.driver.size)
        self.bottom_scope = Scope(
            *tuple(get_proportion_pos(self.screen_scope, (675 / 1920, 1020 / 1080), (1000 / 1920, 1020 / 1080)))
        )
        self.right_scope = Scope(*tuple(get_proportion_pos(self.screen_scope, (1855 / 1920, 580 / 1080), (1, 1))))
        self.right_middle_scope = Scope(
            *tuple(get_proportion_pos(self.screen_scope, (1535 / 1920, 635 / 1080), (1535 / 1920, 835 / 1080)))
        )
        # 可点击范围列表，可以在某功能开始时进行适当更改
        self.scopes = (self.bottom_scope, self.right_scope, self.right_middle_scope)

    # 结束
    def _end_(self, invite=False):
        """
        判断并点击界面跳过结算界面(旧版本宝箱结算)
        :return: 结算结果
        """
        # 等待结束
        module_images = self.images.公共
        end_flag_images = [
            module_images["战斗胜利.png"],
            module_images["战斗失败.png"],
            module_images["结束标志.png"],
            module_images["贪吃鬼.png"],
            module_images["宝箱.png"],
            module_images["宝箱2.png"],
        ]
        while True:
            end_sign = None  # 结算成功标志
            self.auto.delay()
            self.driver.screenshot()  # 截图
            # 一旦检测到结算标志进入循环,再次检测不到退出
            while any(map(self.auto.match, end_flag_images)):
                self.logger.info("检测到结算页面")
                end_sign = True
                # 默认邀请队友
                if invite:
                    if self._invite_():
                        break
                if self.auto.match(module_images["战斗失败.png"]):
                    self.logger.info("检测到战斗失败")
                    end_sign = False

                pos = random.choice((self.bottom_scope, self.right_scope, self.right_middle_scope)).randomPos()
                self.logger.info(f"点击屏幕:{pos}")
                self.driver.click(pos)
                self.auto.delay((0.5, 0.8))
                self.driver.screenshot()  # 截图
            if end_sign is not None:  # 结算后跳出结算循环
                self.logger.info("结算成功")
                return end_sign

    # 准备
    @threading_timeoutable(default=False)
    def _ready_(self):
        """
        准备
        :return: 是否成功准备
        """
        self.auto.delay((1, 1.5))
        while True:
            self.driver.screenshot()  # 截图
            while self.auto.match(self.images.公共["准备.png"]):
                self.driver.screenshot()  # 截图
                self.auto.match_touch(self.images.公共["准备.png"])
                return True

    # 等待队伍满员
    @threading_timeoutable(default=False)
    def _wait_full_team(self):
        """
        用于检测队伍成员是否全部进入
        :return:
        """
        self.driver.screenshot()
        # 检测满员标志，不出现则代表满员跳出检测
        while self.auto.match(self.images.组队["满队标志.png"]):
            self.driver.screenshot()
            self.auto.delay((0.3, 0.5))
        # 再次检测减少误差
        while self.auto.match(self.images.组队["满队标志.png"]):
            self.driver.screenshot()
            self.auto.delay((0.3, 0.5))
        return True

    # 开启默认邀请
    def _invite_(self):
        """
        开启默认邀请
        :return: 是否开启默认邀请成功
        """
        if self.auto.match_touch(self.images.组队["默认邀请.png"]):
            self.auto.delay()
            if self.auto.match_touch(self.images.公共["确定.png"]):
                self.logger.info("开启默认邀请")
                return True
            else:
                self.logger.warning("默认邀请失败")
                return False

    # 开启接受默认邀请
    @threading_timeoutable(default=False)
    def _accept_invite_(self):
        while True:
            if self.auto.match_touch(self.images.组队["同意默认邀请.png"]):
                self.logger.info("同意接受默认邀请")
                return True

    # 正常挑战
    def _combat_(self):
        """
        正常挑战,循环点击挑战与结束
        :return:
        """
        self.driver.screenshot()
        if self.auto.match_touch(self.images.业原火["挑战_业原火.png"]) or self.auto.match_touch(self.images.公共["挑战_菱形.png"]):
            self.logger.info("开始挑战")
            if self._ready_(timeout=8):
                self.logger.warning("准备")
            else:
                self.logger.info("准备超时退出")
            if self._end_():
                self.logger.info("结束挑战")
                return True
        return False

    # 异常检测
    def _check_(self):
        """
        检测异常行为,如悬赏任务等
        :return:
        """
        self.logger.warning("开始执行异常检测")
        self._reward_task_()

    # 协作邀请
    def _reward_task_(self, accept=False):
        if self.auto.match(self.images.异常处理["协作邀请.png"]):
            self.logger.info("检测到协作邀请")
            if accept:
                self.auto.match_touch(self.images.公共["同意.png"])
                self.logger.info("协作邀请已同意")
            else:
                self.auto.match_touch(self.images.公共["拒绝.png"])
                self.logger.info("协作邀请已拒绝")

    # 确认阵容锁定状态
    def _locking_(self):
        """
        确认阵容锁定状态
        :return: bool
        """
        if self.auto.match(self.images.公共["锁.png"]):
            self.logger.info("当前阵容已处于锁定状态")
            return True
        elif self.auto.match_touch(self.images.公共["锁_开.png"]):
            self.logger.info("当前阵容未锁定,已为您自动锁定")
            return True
        else:
            self.logger.info("未检测到阵容锁定按钮")
            return False


class Onmyoji(BaseOnmyoji):
    __doc_all__ = [
        "test",
        "combat",
        "yeyuanhuo",
        "zudui",
        "chengke",
        "jiejie",
        "wanshiwu",
        "chaoguiwang",
    ]

    # 挑战
    def combat(self, count):
        """挑战
        该功能用于正常的副本挑战,可适用于业原火、御灵、单人御魂、单人觉醒等场景。需要处于相应场景下,有该场景的挑战按钮。
        :param count: 挑战的次数
        :return:
        """
        self.logger.info("任务: 挑战")
        i = 0
        while i < count:
            if self._combat_():
                i += 1
                self.logger.info("当前为第{}次挑战".format(i))
        self.logger.info("任务结束，总共进行了{}次挑战".format(i))

    # 业原火
    def yeyuanhuo(self, tan=0, zen=0, chi=0):
        """业原火
        该功能用于业原火副本。可以选择贪嗔痴不同的挑战次数。需要处于庭院或业原火挑战界面。
        :param tan: 贪的数量
        :param zen: 嗔的数量
        :param chi: 痴的数量
        :return:
        """
        module_images = self.images.业原火
        self.logger.info("任务: 业原火")
        option = list("贪嗔痴")
        options = {"贪": int(tan), "嗔": int(zen), "痴": int(chi)}
        for category in option:
            self.logger.info("%s\t%s" % (category, options[category]))
        self.driver.screenshot()
        # 进入业原火界面
        for i in range(5):
            if self.auto.match_touch(self.images.主页["探索.png"]):
                self.logger.info("进入探索页面")
                self.auto.delay()
                self.driver.screenshot()
                if self.auto.match_touch(self.images.公共["御魂.png"]):
                    self.logger.info("进入御魂页面")
                    self.auto.delay()
                    pos = Match.get_ratio_pos(self.driver.screen, [0.6, 0.3], [0.8, .75])
                    self.logger.info(pos)
                    self.driver.click(pos)
                    self.logger.info("进入业原火页面")
                    break
        # 检查是否锁定阵容
        self._locking_()
        # 开始业原火流程
        for category in option:
            count = options[category]
            if count:
                if self.auto.match_touch(module_images[f"{category}.png"]):
                    self.logger.info(f"切换至: {category}")
                i = 0
                while i < count:
                    if self._combat_():
                        i += 1
                        self.logger.info("当前为第%s次%s" % (i, category))
                self.logger.info("总共进行了%s次%s" % (i, category))

    # 组队
    def zudui(self, count, full):
        """组队司机
        该功能用于正常的组队挑战。可适应于组队御魂、觉醒等，需要先手动组队并勾选默认邀请。
        :param count: 组队的次数
        :param full: 是否为满队
        :return:
        """
        module_images = self.images.组队
        self.logger.info("任务：组队司机")
        self.logger.info("目标：{}次".format(count))
        self.logger.info("参数：是否等待满员{}".format(full))
        i = 0
        while i < int(count):
            self.driver.screenshot()
            if self._locking_():
                if self.auto.match(module_images["组队开始标志.png"]):
                    # 等待队伍满员
                    if full:
                        self.logger.info("等待队伍满员")
                        if self._wait_full_team(timeout=15):
                            self.logger.info("队伍已满员")
                        else:
                            self.logger.warning("等待队伍满员超时退出")
                    if self.auto.match_touch(module_images["挑战.png"]):
                        self.logger.info("开始战斗")
                        if self._ready_(timeout=8):
                            self.logger.warning("准备")
                        else:
                            self.logger.info("准备超时退出")
                        if self._end_(invite=True):
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
        """组队乘客
        该功能用于正常的组队挑战。可适应于组队御魂、觉醒等，需要先勾选自动接收邀请。
        :param count: 组队的次数
        :param accept: 是否接受默认邀请
        :type accept: bool
        :return:
        """
        self.logger.info("任务：组队乘客")
        self.logger.info("目标：{}次".format(count))
        i = 0
        while i < int(count):
            self.driver.screenshot()
            if accept:
                if self._accept_invite_(timeout=8):
                    accept = False
                else:
                    self.logger.warning("没有收到队友的默认邀请")
            if self._ready_(timeout=5):
                self.logger.warning("准备")
            else:
                self.logger.info("准备超时退出")
            if self._end_():
                i += 1
                self.logger.info("当前已进行{}次".format(i))

    # 结界突破
    def jiejie(self):
        """结界突破
        该功能用于结界突破。目前功能仍使用的老旧代码，请谨慎使用。
        :return:
        """
        module_images = self.images.结界
        self.logger.info("任务: 结界突破")
        # 结界对象大小
        jiejie_object_width = 455
        jiejie_object_height = 160
        while True:
            self.driver.screenshot()
            # 检查是否在结界界面
            if not (self.auto.match(module_images["突破标志.png"]) or self.auto.match(module_images["突破标志2.png"])):
                self.logger.warning("当前不在结界界面")
                if self.auto.match_touch(self.images.公共["结界突破.png"]):
                    self.logger.info("已自动进入结界突破界面")
                    self.driver.screenshot()
                else:
                    self.logger.error("无法进入结界突破界面,任务停止")
                    break
            # 匹配目标
            screen = self.driver.screen
            self.driver.threshold = 0.98
            # 判断当前次数
            if self.auto.match(module_images["寮次数.png"]):
                self.logger.warning("突破次数不足")
                # 等待15-20分钟
                self.auto.delay((15 * 60, 20 * 60))
            self.driver.threshold = 0.9
            self.logger.info("获取结界目标")
            pos_list = Match.get_match_pos(self.driver.screen, module_images["突破对象标志2.png"], 0.92)
            if pos_list:
                self.logger.info("获取到{}个结界目标".format(len(pos_list)))
                # 开始遍历结界目标
                for pos in pos_list:
                    self.driver.screenshot()
                    if not self.auto.match_touch(self.images.公共["宝箱.png"]):
                        self.auto.match_touch(self.images.公共["宝箱2.png"])
                    pos_begin = (pos[1][0] - jiejie_object_width, pos[1][1] - jiejie_object_height)
                    pos_end = pos[1]
                    self.logger.info("开始节点：{}结束节点：{}".format(pos_begin, pos_end))
                    # 判断坐标真实有效,排除显示不全的目标
                    if pos_begin[0] > 0 and pos_begin[1] > 0:
                        jiejie_img = screen[pos_begin[1]:pos_end[1], pos_begin[0]:pos_end[0]]
                        Match.show_img(jiejie_img, time=800)
                        if Match.match(jiejie_img, module_images["败北.png"]):
                            self.logger.info("目标状态：败北")
                        elif Match.match(jiejie_img, module_images["击破.png"]):
                            self.logger.info("目标状态：击破")
                        else:
                            self.logger.info("目标状态：未突破")
                            self.driver.click(fun.get_random_pos(*pos))  # ####
                            self.auto.delay()
                            self.driver.screenshot()
                            if self.auto.match_touch(module_images["进攻.png"]):
                                self.logger.info("开始突破")
                                self.driver.screenshot()
                                if self._end_():
                                    self.logger.info("突破成功")
                                    self.auto.delay()
                                    break
                                else:
                                    self.logger.info("突破失败")
                            else:
                                self.logger.info("未检测到结界挑战页面")
                    else:
                        self.logger.warning("无效的坐标")
                # 遍历完后滑动列表
                else:
                    # self.driver.slide_event(1200, 875, dc="u", distance=700)
                    self.driver.swipe(Scope((1200, 875), (1200, 175)), 200)
                    self.auto.delay()
            else:
                self.logger.warning("未获取到结界目标")

    # 万事屋
    def wanshiwu(self):
        """万事屋自动领取
        该功能用于万事屋活动。用于自动领取奖励，需要处于庭院或万事屋主界面。
        :return:
        """
        module_images = self.images.万事屋
        # 进入万事屋
        self.driver.screenshot()
        self.logger.info("尝试进入万事屋")
        self.auto.match_touch(module_images["进入万事屋.png"])
        self.auto.delay()
        self.driver.screenshot()
        self.logger.info("尝试进入事件")
        self.auto.match_touch(module_images["进入事件.png"])
        self.auto.delay()
        # 自动领取奖励主循环
        while True:
            self.driver.screenshot()
            # 异常检查
            self._check_()
            # 检测突发状况Buff
            if self.auto.match(module_images["事件_突发状况.png"]):
                self.logger.info("检测到突发状况Buff")
                self.auto.match_touch(module_images["事件_一键领取.png"])
            # 检测未关闭的奖励页面
            if self.auto.match(module_images["事件_奖励.png"]):
                self.auto.match_touch(module_images["事件_一键领取.png"])
            # 领取循环
            self.auto.delay()
            self.driver.screenshot()
            if self.auto.match_touch(module_images["事件_一键领取.png"]):
                self.logger.info("一键领取奖励")
                start = time.time()
                while True:
                    self.auto.delay()
                    self.driver.screenshot()
                    if self.auto.match(module_images["事件_奖励.png"]):
                        self.auto.match_touch(module_images["事件_一键领取.png"])
                        self.logger.info("成功领取奖励")
                        # 检测无法自动领取的奖励
                        # pass
                        self.logger.info("进入等待")
                        break
                    if time.time() - start > 15:
                        self.logger.warning("点击了一键领取奖励，但未检测到奖励页面。")
                        break
                # 等待5-10分钟
                self.auto.delay((60 * 5, 60 * 10))
            else:
                self.logger.error("不在程序运行所需场景，请切换至{万事屋=>事件}场景。")

    # 超鬼王
    def chaoguiwang(self):
        """超鬼王
        该功能用于超鬼王活动。通过挑战单人觉醒刷超鬼王并自动击杀。需要预先配置好觉醒挑战层数和超鬼王阵容。
        可能会因为网络波动而错过检测到超鬼王弹出界面，导致错过该超鬼王，并在该超鬼王存在期间持续挑战觉醒。
        :return:
        """
        module_images = self.images.超鬼王
        rouse_count = 0
        count = 0
        kyLin = ["火麒麟.png", "风麒麟.png", "水麒麟.png", "雷麒麟.png"]
        self.logger.info("任务: 超鬼王")
        while count < 100:
            self.driver.screenshot()  # 截图
            self.auto.match_touch(self.images.公共["觉醒.png"])  # 匹配点击图片
            self.auto.delay()
            self.driver.screenshot()  # 截图
            self.auto.match_touch(self.images.觉醒[random.choice(kyLin)])  # 选择列表中随机一个进行点击
            if self._locking_():
                self.logger.info("当前阵容已处于锁定状态")

                # 进入循环挑战觉醒阶段
                self.logger.info("进入循环挑战觉醒阶段")
                while True:
                    self.auto.delay()
                    self.driver.screenshot()  # 截图
                    if self.auto.match_touch(module_images["发现超鬼王.png"]):
                        self.auto.match_touch(module_images["发现超鬼王.png"])
                        self.logger.info("发现超鬼王")
                        break  # 跳出觉醒循环
                    if self.auto.match_touch(self.images.觉醒["挑战.png"]):
                        self.logger.info("开始挑战")
                        # 等待挑战结束
                        if self._end_():
                            rouse_count += 1
                            self.logger.info("当前已进行%s次觉醒" % rouse_count)

                # 进入超鬼王阶段
                self.logger.info("进入超鬼王阶段")
                while True:
                    self.auto.delay()
                    self.driver.screenshot()  # 截图
                    while True:
                        self.auto.delay()
                        self.driver.screenshot()  # 截图
                        if not self.auto.match_touch(module_images["挑战.png"]):
                            break
                        self.logger.info("开始挑战超鬼王")
                        # 准备
                        if self._ready_(timeout=8):
                            self.logger.warning("准备")
                        else:
                            self.logger.info("准备超时退出")
                        # 等待结束
                        if self._end_():
                            count += 1
                    if self.auto.match_touch(self.images.公共["返回.png"]):
                        self.logger.info("击败超鬼王,跳出超鬼王阶段")
                        self.logger.info("当前已击败%s只鬼王" % count)
                        break

    # 测试
    def test(self):
        """测试
        该功能仅用于测试
        :return:
        """
        self.logger.info("测试函数开始执行")
        for _ in range(10):
            self.logger.info("测试函数执行")
            self.auto.delay()
        self.logger.info("测试函数执行结束")


# noinspection PyTypeChecker
def _test():
    driver = choose_driver(MiniDriver.driver_list())
    if driver:
        onmyoji = Onmyoji(MiniDriver(driver.serial))
        # onmyoji.zudui(1234)
        onmyoji.combat(500)
        # onmyoji.yeyuanhuo(12, 34, 56)
        # onmyoji.jiejie()


if __name__ == '__main__':
    _test()
