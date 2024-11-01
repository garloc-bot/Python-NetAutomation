import socket

ip = input("IP to scan: ")

for port in range(1, 65535):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    result = sock.connect_ex((ip, port))

    if result == 0:
        print("This port is OPEN: " + str(port))
        sock.close()