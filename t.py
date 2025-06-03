import socket
import threading
import time

# آدرس و پورت سرور
HOST = 'localhost'
PORT = 12345
ADDR = (HOST, PORT)

# ایجاد سوکت
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(4)

print("در انتظار اتصال...")
conn, addr = server.accept()
print(f"متصل به {addr}")

# ارسال داده به صورت بایت
def send_data():
    try:
        while True:
            send_data = input(">> ")
            if send_data.lower() == 'exit':
                break
            conn.send(send_data.encode('utf-8'))  # تبدیل به بایت با encode()
    finally:
        conn.close()
        server.close()

def recv_data():
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data.decode('utf-8'))
            time.sleep(5)
    finally:
        conn.close()

# ایجاد و شروع تردها
threading.Thread(target=send_data).start()
threading.Thread(target=recv_data).start()
