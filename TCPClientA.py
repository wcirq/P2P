# -*- coding: utf-8 -*- 
# @File TCPClient
# @Time 2021/12/2
# @Author wcy
# @Software: PyCharm
# @Site
import socket
import threading
import time


# 连接服务器
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# serverAddress = ('106.15.234.102', 11111)
serverAddress = ('192.168.106.226', 11111)

s.connect(serverAddress)
myAddress = s.getsockname()  # 本机ip端口
chain = input('连接口令：')
send = ('#connectChain*' + chain).encode()
s.sendall(send)
myPeer = eval(s.recv(2048).decode())  # peer ip端口
print('myAddress: ', myAddress)
print('got myPeer: ', myPeer)
s.close()

# 等待对方打洞
time.sleep(10)

# 发起TCP连接
print('正在发起连接请求')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(myAddress)
s.connect(myPeer)


# 聊天
def sendToMyPeer():
    while True:
        send_text = input("我方发送：")
        s.sendall(send_text.encode())


def recFromMyPeer():
    while True:
        message = s.recv(2048).decode()
        print('\r对方回复：' + message + '\n我方发送：', end='')


sen_thread = threading.Thread(target=sendToMyPeer)
rec_thread = threading.Thread(target=recFromMyPeer)

rec_thread.start()
sen_thread.start()

sen_thread.join()
rec_thread.join()
