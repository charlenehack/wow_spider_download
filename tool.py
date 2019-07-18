import socket, requests, random, time, psutil, logging

s = socket.socket

def get_ip():
    '''获取本机所有网卡地址加入列表'''
    iplist = list()
    info = psutil.net_if_addrs()
    for k,v in info.items():
        if ':' not in v[0][1] and not v[0][1] == '127.0.0.1' and v[0][1] != '192.168.1.13':
            iplist.append(v[0][1])

    return iplist

def bind_ip(*args):
    get_ip()
    sock = s()
    addr = random.choice(ip_list)
    sock.bind((addr, 0))

    return sock

#while True:
#    socket.socket = bind_ip
#    r = requests.get('http://www.ip.cn')
#
#    print(r.content)
#    time.sleep(2)

def logger():
    logger = logging.getLogger('main')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('download.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
