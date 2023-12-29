import os
import socket
import threading
import time

import stun

from punch.base import NatType
from punch.symmetry_plaincone import SymmetryPlainconePunch

STOP_RECEIVE = False
BUFFER_SIZE = 256


def send_file(s, host_port, file_path):
    path, file_name = os.path.split(file_path)
    data = bytes(f"[0]{file_name}", encoding="utf8")
    s.sendto(data, host_port)
    res, server_addr = s.recvfrom(BUFFER_SIZE)
    file_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as f:
        total = 0
        count = 0
        while True:
            data = f.read(BUFFER_SIZE)
            if str(data) != "b''":
                # 发生文件片段
                s.sendto(data, host_port)
                # res, server_addr = s.recvfrom(BUFFER_SIZE)
                count += 1
            else:
                # 结束
                data = bytes(f"[1]{file_name}", encoding="utf8")
                while True:
                    try:
                        s.settimeout(1.5)
                        s.sendto(data, host_port)
                        res, server_addr = s.recvfrom(BUFFER_SIZE)
                        break
                    except Exception as e:
                        time.sleep(0.1)
                        continue
                    finally:
                        s.settimeout(99)
                break
            total += 1
            print(f"\r{round(total * BUFFER_SIZE / file_size * 100, 2)}% [{total * BUFFER_SIZE}/{file_size}]", end="")
    print(f"count: {count}")
    print("send file ok")


def receive_file(s, host_port, file_name):
    print(f"准备接收文件 {file_name}")
    f = open(file_name, 'wb')
    count = 0
    while True:
        data, client_addr = s.recvfrom(BUFFER_SIZE)
        if data == b"":
            continue
        if data[:3] == b"[1]":
            print(f"文件接收完成 {file_name}")
            f.close()
            s.sendto('ok'.encode('utf-8'), host_port)
            break
        else:
            f.write(data)
            # s.sendto('ok'.encode('utf-8'), host_port)
            count += 1
    print(f"count: {count}")
    print("接收完成", end="")


def sendToMyPeer(s, peerHostPort):
    global STOP_RECEIVE
    # 发送聊天信息
    while True:
        send_text = input(f"我方发送：")
        if os.path.isfile(send_text):
            STOP_RECEIVE = True
            # 是文件就发送文件
            file_path = send_text
            time.sleep(1.5)
            s.settimeout(99)
            send_file(s, peerHostPort, file_path)
            STOP_RECEIVE = False
            s.settimeout(0.1)
        else:
            s.sendto(send_text.encode(), peerHostPort)


def recFromMyPeer(s, peerHostPort):
    while True:
        if STOP_RECEIVE:
            time.sleep(0.1)
            continue
        try:
            message, senderInfo = s.recvfrom(BUFFER_SIZE)
            message = message.decode()
            if message:
                print(f'\r(from {senderInfo}) 对方回复：{message}\n我方发送：', end='')
            if message[:3] == "[0]":
                s.settimeout(99)
                file_name = message[3:]
                print(f"开始接收文件1 {file_name}")
                s.sendto('ok'.encode('utf-8'), peerHostPort)
                print(f"开始接收文件2 {file_name}")
                receive_file(s, peerHostPort, file_name)
                s.settimeout(0.1)
        except Exception as e:
            continue


def main():
    nat_type, external_ip, external_port = stun.get_ip_info()
    if nat_type == stun.FullCone:
        nat_type = NatType.FULL_CONE
    elif nat_type == stun.RestricNAT:
        nat_type = NatType.ADDRESS_RESTRICTED_CONE
    elif nat_type == stun.RestricPortNAT:
        nat_type = NatType.PORT_RESTRICTED_CONE
    elif nat_type == stun.SymmetricNAT:
        nat_type = NatType.SYMMETRIC

    print("NAT TYPE:", nat_type)

    # host = "192.168.88.226"
    host = "106.15.234.102"
    port = 11111
    host_port = (host, port)
    s, peerHostPorts = SymmetryPlainconePunch(
        "q",
        host,
        nat_type=nat_type
    ).punch()

    # s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(1)

    sen_thread = threading.Thread(target=sendToMyPeer, args=(s, peerHostPorts))
    rec_thread = threading.Thread(target=recFromMyPeer, args=(s, peerHostPorts))

    sen_thread.start()
    rec_thread.start()

    sen_thread.join()
    rec_thread.join()


if __name__ == '__main__':
    main()
