import socket


if __name__ == '__main__':
    host = socket.gethostbyname_ex("www.wcirq.com")
    hostname = socket.gethostname()
    addrinfo = socket.getaddrinfo("106.15.234.102", 80)
    addrinfo = socket.gethostbyaddr(hostname)
    print(addrinfo)