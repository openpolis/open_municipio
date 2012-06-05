import socket

def netcat(hostname, port, content):
    """
    netcat (nc) implementation in python
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.sendall(content)
    s.shutdown(socket.SHUT_WR)
    res = ''
    while 1:
        data = s.recv(1024)
        if data == "":
            break
        res += data
    s.close()
    return res


