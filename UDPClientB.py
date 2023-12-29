# -*- coding: utf-8 -*- 
# @File UDPClient
# @Time 2021/12/2
# @Author wcy
# @Software: PyCharm
# @Site
import os
import socket
import threading
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.settimeout(1)
serverAddress = ('192.168.88.226', 11111)
# serverAddress = ('106.15.234.102', 11111)

# 连接服务器
chain = input('连接口令：')
send = ('#connectChain*' + chain).encode()
s.sendto(send, serverAddress)
message = eval(s.recvfrom(2048)[0].decode())
myPeerAPort1 = message[0]
signature = str(message[1])
print('got myPeer: ', myPeerAPort1)
myPeerAPort2 = None

peerConnected = False
stop_receive = False


def send_heartbeat():
    while True:
        s.sendto("".encode(), myPeerAPort2)
        time.sleep(10)


# 先连接myPeer，再互发消息
def send_file(host_port, file_path):
    path, file_name = os.path.split(file_path)
    data = bytes(f"[0]{file_name}", encoding="utf8")
    s.sendto(data, host_port)
    print("start recvfrom")
    res, server_addr = s.recvfrom(1024)
    print("end recvfrom")
    with open(file_path, 'rb') as f:
        print("send file")
        while True:
            data = f.read(1024)
            if str(data) != "b''":
                # 发生文件片段
                s.sendto(data, host_port)
                res, server_addr = s.recvfrom(1024)
            else:
                # 结束
                data = bytes(f"[1]{file_name}", encoding="utf8")
                s.sendto(data, host_port)
                res, server_addr = s.recvfrom(1024)
                break
    print("send file ok")


def receive_file(host_port, file_name):
    global stop_receive
    print(f"准备接收文件 {file_name}")
    f = open(file_name, 'wb')
    while True:
        if stop_receive:
            time.sleep(10)
            continue
        data, client_addr = s.recvfrom(1024)
        if data == b"":
            continue
        if data[:3] == "[1]":
            print(f"文件接收完成 {file_name}")
            f.close()
            s.sendto('ok'.encode('utf-8'), host_port)
            break
        else:
            f.write(data)
            s.sendto('ok'.encode('utf-8'), host_port)
    print("接收完成", end="")



# 先连接myPeer，再互发消息
def sendToMyPeer():
    # 发送包含签名的连接请求
    global peerConnected, myPeerAPort2
    while True:
        s.sendto(signature.encode(), myPeerAPort1)
        if peerConnected:
            break
        time.sleep(1)

    # threading.Thread(target=send_heartbeat).start()
    # 发送聊天信息
    while True:
        send_text = input(f"(to {myPeerAPort2}) 我方发送：")
        if os.path.exists(send_text):
            # 是文件就发送文件
            file_path = send_text
            send_file(myPeerAPort2, file_path)
        else:
            s.sendto(send_text.encode(), myPeerAPort2)


def recFromMyPeer():
    # 接收请求并验证签名or接收聊天信息
    global peerConnected, myPeerAPort2, stop_receive
    end_burrowing = False
    while True:
        try:
            message, senderInfo = s.recvfrom(2048)
        except socket.timeout:
            print("Didn't receive data! [Timeout 5s]")
            continue
        message = message.decode()
        if message == signature and not end_burrowing:
            if not peerConnected:
                myPeerAPort2 = senderInfo
                s.sendto(signature.encode(), senderInfo)  # 往A的新端口发生探测包
                print('connected successfully')
                end_burrowing = True
            peerConnected = True
        elif peerConnected:
            if message:
                print(f'\r(from {senderInfo}) 对方回复：{message}\n我方发送：', end='')
            if message[:3] == "[0]":
                stop_receive = True
                time.sleep(1.1)
                file_name = message[3:]
                print(f"开始接收文件 {file_name}")
                receive_file(myPeerAPort2, file_name)
                stop_receive = False


sen_thread = threading.Thread(target=sendToMyPeer)
rec_thread = threading.Thread(target=recFromMyPeer)

sen_thread.start()
rec_thread.start()

sen_thread.join()
rec_thread.join()