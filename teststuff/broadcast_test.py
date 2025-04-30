import socket
test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
try:
    test_sock.sendto(b'test', ('255.255.255.255', 47808))
    print("Broadcast möglich")
except Exception as e:
    print(f"Broadcast-Problem: {e}")
test_sock.close()