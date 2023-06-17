# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : 多线程.py
# @Project : python-modules
# @Software: PyCharm
import math
import threading


class ExtendThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        super(ExtendThread, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)

    def get_result(self):
        try:
            return self.result
        except Exception as ex:
            print(ex)
            return None


def aa(data: list, callback, *args, **kwargs):
    exist = []
    for cs in range(math.ceil(len(data) / 10)):
        _min = cs * 10
        _max = _min + 10
        p = []
        for item in data[_min:_max]:
            args = (item,) + args
            p.append(ExtendThread(callback, *args, **kwargs))
        for j in p:
            j.start()
        for j in p:
            j.join()
            res = j.get_result()
            exist.append(res)


def bb(data, *args, **kwargs):
    print(args)
    print('kwargs::', kwargs)
    print('item::', data)
    cc(*args, **kwargs)


def cc(*args, **kwargs):
    print('c--args::', args)
    print('c--kwargs::', kwargs)


def main():
    data = []
    if data:
        print(data)
    else:
        print(11)

    data = [
        {'a': 10}
    ]
    # bb(data, 1, 2, 3, ff=11, dd=22)
    # print('****************************************')
    aa(data, bb, 1, 2, 3, ff=11, dd=22)


if __name__ == '__main__':
    main()
