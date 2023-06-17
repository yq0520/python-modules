# @Author  : 记不起的回忆
# @email   : 836875692@qq.com
# @File    : 网卡速度检测.py
# @Project : python-modules
# @Software: PyCharm
import time
import psutil
import datetime


def get_key():
    key_info = psutil.net_io_counters(pernic=True).keys()

    recv = {}
    sent = {}

    for key in key_info:
        recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)
        sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)

    return key_info, recv, sent


def get_rate(func):
    key_info, old_recv, old_sent = func()

    time.sleep(1)

    key_info, now_recv, now_sent = func()

    net_in = {}
    net_out = {}

    for key in key_info:
        # float('%.2f' % a)
        net_in.setdefault(key, float('%.2f' % ((now_recv.get(key) - old_recv.get(key)) / 1024 / 1024 * 8)))
        net_out.setdefault(key, float('%.2f' % ((now_sent.get(key) - old_sent.get(key)) / 1024 / 1024 * 8)))

    return key_info, net_in, net_out


def main_rate():
    while 1:
        try:
            time.sleep(1)
            key_info, net_in, net_out = get_rate(get_key)

            for key in key_info:
                # lo 是linux的本机回环网卡，以太网是win10系统的网卡名
                # if key == '以太网 3':
                print('%s\nInput:\t %-5sKB/s\nOutput:\t %-5sKB/s\n' % (key, net_in.get(key), net_out.get(key)))
        except KeyboardInterrupt:
            exit()


def date_time_m():
    start_time = datetime.datetime.now()
    t1 = time.time()
    time.sleep(1)
    end_time = datetime.datetime.now()
    ti = (end_time - start_time).microseconds
    print(ti)
    t2 = time.time()
    ti1 = t2 - t1
    print(ti1)


def main():
    main_rate()
    net_info = psutil.net_io_counters(pernic=True)
    for key, value in net_info.items():
        print(key)
        print(value)
    # print(net_info)


if __name__ == '__main__':
    main()
