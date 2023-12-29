import os
import socket
import threading
import time
from .base import NatType


class SymmetryPlainconePunch(object):

    def __init__(self, chain, server_address, server_port=11111, nat_type: NatType = NatType.FULL_CONE, timeout=9999):
        print(nat_type)
        self.server_address = server_address
        self.server_port = server_port
        self.nat_type = nat_type
        self.timeout = timeout
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # self.s.settimeout(timeout)
        self.serverAddressPort = (server_address, server_port)
        send = ('#connectChain*' + chain).encode()
        self.s.sendto(send, self.serverAddressPort)
        message = eval(self.s.recvfrom(2048)[0].decode())
        self.peerHostPorts = [message[0]]
        self.signature = str(message[1])
        self.punch_ok = False

    def _receive(self):
        while True:
            try:
                message, sender_info = self.s.recvfrom(2048)
            except Exception as e:
                continue
            message = message.decode()
            if message == self.signature:
                if sender_info == self.peerHostPorts[0]:
                    if self.nat_type > NatType.ADDRESS_RESTRICTED_CONE:
                        print('connected successfully')
                        break
                    else:
                        continue
                else:
                    self.peerHostPorts.append(sender_info)
                    self.s.sendto(self.signature.encode(), sender_info)  # 往A的新端口发生探测包
                    print('connected successfully')
                    break
        self.punch_ok = True

    def _send(self):
        while True:
            self.s.sendto(self.signature.encode(), self.peerHostPorts[0])
            if self.punch_ok:
                break
            time.sleep(1)

    def _send_heartbeat(self):
        while True:
            self.s.sendto("".encode(), self.peerHostPorts[-1])
            time.sleep(10)

    def punch(self):
        sen_thread = threading.Thread(target=self._send)
        rec_thread = threading.Thread(target=self._receive)

        sen_thread.start()
        rec_thread.start()

        sen_thread.join()
        rec_thread.join()

        threading.Thread(target=self._send_heartbeat).start()
        print(self.peerHostPorts)
        return self.s, self.peerHostPorts[-1]


if __name__ == '__main__':
    peerHostPorts = SymmetryPlainconePunch(
        "q",
        "106.15.234.102",
        # nat_type=NatType.FULL_CONE
        nat_type=NatType.SYMMETRIC
    ).punch()
    print("peerHostPorts", peerHostPorts)
