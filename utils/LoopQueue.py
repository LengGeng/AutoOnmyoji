import threading
import time
from queue import Queue


class LoopQueue:
    def __init__(self, maxsize: int = 10):
        self.maxsize = maxsize
        self.__queue = Queue(maxsize)

    def put(self, item):
        size = self.__queue.qsize()
        if size >= self.maxsize:
            for _ in range(size - self.maxsize + 1):
                self.__queue.get()
        # 添加新数据
        self.__queue.put(item)

    def get(self):
        return self.__queue.get()

    def size(self) -> int:
        return self.__queue.qsize()

    def empty(self) -> bool:
        return self.__queue.empty()


def _producer(interval):
    for i in range(100):
        lq.put(i)
        print(f"producer put {i} at {time.time()}")
        time.sleep(interval)


def _consumer(name, interval):
    for i in range(100):
        print(f"producer({name}) wait get({i})")
        item = lq.get()
        print(f"producer({name}) get {item} at {time.time()}")
        time.sleep(interval)


def _test_thread():
    p = threading.Thread(target=_producer, args=(0.1,))
    c1 = threading.Thread(target=_consumer, args=("C1", 0.2,))
    c2 = threading.Thread(target=_consumer, args=("C2", 0.3,))
    c3 = threading.Thread(target=_consumer, args=("C3", 0.4,))
    p.start()
    c1.start()
    c2.start()
    c3.start()
    p.join()
    c1.join()
    c2.join()
    c3.join()


def _test_get():
    for i in range(100):
        lq.put(i)

    def t1():
        while not lq.empty():
            print(f"{threading.currentThread().getName()}:{lq.get()}")

    threading.Thread(target=t1).start()
    threading.Thread(target=t1).start()
    threading.Thread(target=t1).start()
    threading.Thread(target=t1).start()


def _test():
    _test_get()
    _test_thread()


if __name__ == '__main__':
    lq = LoopQueue(50)
    _test()
