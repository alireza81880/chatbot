import socket
import threading

HOST = 'localhost'
PORT = 12345

class ChatClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))
        self.running = True
        self.lock = threading.Lock()

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    print(f"\n[پیام جدید] {message}")
                    print(">> ", end="", flush=True)  # نمایش مجدد prompt
            except Exception as e:
                print(f"\nخطا در دریافت: {str(e)}")
                self.stop()

    def send(self):
        while self.running:
            try:
                message = input(">> ")
                self.client.send(message.encode('utf-8'))
                if message.lower() == 'exit':
                    self.stop()
                    break
            except Exception as e:
                print(f"خطا در ارسال: {str(e)}")
                self.stop()

    def stop(self):
        self.running = False
        self.client.close()

if __name__ == "__main__":
    client = ChatClient()
    receive_thread = threading.Thread(target=client.receive)
    send_thread = threading.Thread(target=client.send)
    
    receive_thread.daemon = True
    send_thread.daemon = True
    
    receive_thread.start()
    send_thread.start()
    
    receive_thread.join()
    send_thread.join()