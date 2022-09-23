from multiprocessing import Process, freeze_support

import psutil
from flask import Flask, make_response, request

from Onmyoji import Onmyoji
from drives import AdbDriver, MiniDriver
from webbrowser import open as browser_open
from run import OnmyojiRun, get_fun
from utils.ImageUtils import cv2bytes
from utils.docs import Docs

app = Flask("AutoOnmyojiUI", static_url_path="/")

ACTIVITY = {}


# 暂停进程
def suspendProcess(process: Process):
    pid = process.pid
    print('进程暂停 进程编号 %s ' % pid)
    p = psutil.Process(pid)
    p.suspend()


# 唤醒进程
def wakeProcess(process: Process):
    pid = process.pid
    print('进程恢复 进程编号 %s ' % pid)
    p = psutil.Process(pid)
    p.resume()


# 关闭进程
def finishProcess(process: Process):
    pid = process.pid
    print('进程关闭 进程编号 %s ' % pid)
    process.terminate()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/devices")
def devices():
    device_list = [[device.serial, "device"] for device in MiniDriver.driver_list()]
    return {
        "code": 0,
        "data": device_list
    }


@app.get("/screen/<string:serial>")
def screen(serial):
    driver = AdbDriver(serial)
    driver.screenshot()
    return make_response(cv2bytes(driver.screen))


@app.get("/functions")
def functions():
    return {
        "code": 0,
        "data": get_fun()
    }


@app.post("/create")
def create_task():
    option = request.get_json()
    device = option['device']
    fun = option['fun']
    args = option.get("args") or ()
    kwargs = option.get("kwargs") or {}

    if device in ACTIVITY:
        p: Process = ACTIVITY[device]["process"]
        if p.is_alive():
            return {"code": 1001, "msg": "该设备已有执行的任务!"}

    task = Process(target=OnmyojiRun, args=(device, fun, *args), kwargs=kwargs)
    ACTIVITY[device] = {"fun": fun, "process": task, "suspend": False}
    task.start()
    print("开始执行任务")

    return {
        "code": 0,
        "message": "success"
    }


@app.post("/finish")
def finish_task():
    device = request.get_json()['device']
    if device in ACTIVITY and ACTIVITY[device]["process"].is_alive():
        process: Process = ACTIVITY[device]["process"]
        finishProcess(process)
        return {"data": "success"}
    else:
        return {"code": 500, "mag": "当前设备没有正在执行的任务"}


@app.post("/suspend")
def suspend_task():
    device = request.get_json()['device']
    if device in ACTIVITY and ACTIVITY[device]["process"].is_alive():
        process: Process = ACTIVITY[device]["process"]
        suspend: bool = ACTIVITY[device]["suspend"]
        if not suspend:
            suspendProcess(process)
            ACTIVITY[device]["suspend"] = True
            return {"data": "success"}
    else:
        return {"code": 500, "mag": "当前设备没有正在执行的任务"}


@app.post("/wake")
def wake_task():
    device = request.get_json()['device']
    if device in ACTIVITY and ACTIVITY[device]["process"].is_alive():
        process: Process = ACTIVITY[device]["process"]
        suspend: bool = ACTIVITY[device]["suspend"]
        if suspend:
            wakeProcess(process)
            ACTIVITY[device]["suspend"] = False
            return {"data": "success"}
    else:
        return {"code": 500, "mag": "当前设备没有正在执行的任务"}


@app.get("/actives")
def get_actives():
    actives = []
    if ACTIVITY:
        for device, info in ACTIVITY.items():
            fun = info["fun"]
            process = info["process"]
            suspend = info["suspend"]
            actives.append({'device': device, 'fun': fun, "alive": process.is_alive(), "suspend": suspend})
    return {
        "code": 0,
        "data": actives
    }


if __name__ == "__main__":
    freeze_support()
    browser_open('http://127.0.0.1')
    app.run(port=80)
