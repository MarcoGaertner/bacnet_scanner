import socket
test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    test_sock.bind(('10.48.172.120', 47808))
    print("Port ist verfügbar")
    test_sock.close()
except Exception as e:
    print(f"Port ist nicht verfügbar: {e}")