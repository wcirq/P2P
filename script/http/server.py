import socket
import threading
import time


def server(t_sock, t_add):
    # 循环：为一个客户多次服务
    start = time.time()
    while True:
        try:
            # 从客户端接收http请求
            recv_data = t_sock.recv(1024)
            print(recv_data.decode("gbk"))
            # 给客户端发送http应答，在网页上显示‘你好’
            # http可能面对不同的os，所以约定用\r\n来表示换行
            # http的header和body区分之处：只要出现第一个空行，二者便区分开
            send_data = f"HTTP/1.1 200 OK\r\n\r\n<h1>你好 {t_add} start：{start}</h1>"
            end = time.time()
            if end - start > 5:
                t_sock.send(f"{send_data}\r\n<h2>结束{t_add} start：{start}</h2>".encode("gbk"))
                break
            else:
                # send_data = f"<h1>你好</h1>"
                t_sock.send(send_data.encode("gbk"))
        except Exception as e:
            send_data = f"HTTP/1.1 200 OK\r\n\r\n<h1>你好 {t_add} start：{start} error: {e}</h1>"
            t_sock.send(send_data.encode("gbk"))
    print("end")
    # 关闭服务套接字
    t_sock.close()


def main():
    # 创建tcp套接字
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置当服务器先调用close，即服务器四次挥手后能将资源立即释放，这样就保证了下次运行程序时能
    # 立即连接
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定ip，端口
    tcp_sock.bind(('', 54321))
    # 改为监听套接字
    tcp_sock.listen(128)
    # 循环：可以为多个客户服务
    while True:
        # 使用accept等待客户连接，此时程序阻塞
        # 客户连接后返回两个值，服务套接字和客户端地址
        client_sock, client_add = tcp_sock.accept()

        # 为客户服务，用一个方法来实现，注意参数
        t = threading.Thread(target=server, args=(client_sock, client_add, ))
        t.start()

    # 关闭监听套接字
    tcp_sock.close()


if __name__ == "__main__":
    main()
