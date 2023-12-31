# -*- coding: utf-8 -*- 
# @File server
# @Time 2021/12/2
# @Author wcy
# @Software: PyCharm
# @Site
import socketserver
import json

connList = []


# 连接列表，用来保存一个连接的信息（代号 地址和端口 连接对象）
class Connector(object):  # 连接对象类
    def __init__(self, account, password, addrPort, conObj):
        self.account = account
        self.password = password
        self.addrPort = addrPort
        self.conObj = conObj


class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        print("got connection from", self.client_address)
        register = False
        while True:
            conn = self.request
            data = conn.recv(1024)
            if not data:
                continue
            dataobj = json.loads(data.decode('utf-8'))
            # 如果连接客户端发送过来的信息格式是一个列表且注册标识为False时进行用户注册
            if type(dataobj) == list and not register:
                account = dataobj[0]
                password = dataobj[1]
                conObj = Connector(account, password, self.client_address, self.request)
                connList.append(conObj)
                register = True
                continue
            print(connList)
            # 如果目标客户端在发送数据给目标客服端
            if len(connList) > 1 and type(dataobj) == dict:
                sendok = False
                for obj in connList:
                    if dataobj['to'] == obj.account:
                        obj.conObj.sendall(data)
                        sendok = True
                if sendok == False:
                    print('no target valid!')
            else:
                conn.sendall('nobody recevied!'.encode('utf-8'))
                continue


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('192.168.88.226', 5000), MyServer)
    print('waiting for connection...')
    server.serve_forever()
