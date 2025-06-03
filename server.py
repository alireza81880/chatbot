from tkinter import *
from tkinter import font
import socket
import threading
import queue
from datetime import datetime

COLORS = {
    "background": "#182533",
    "input_bg": "#2a3f5a",
    "text_white": "#ffffff",
    "sent_msg": "#2b5278",
    "received_msg": "#2d4369",
    "timestamp": "#7f8a9a"
}

class TelegramStyleChat:
    def __init__(self, root):
        self.root = root
        self.connections = []
        self.message_queue = queue.Queue()
        self.running = True
        
        # تعریف فونت‌ها
        self.font = font.Font(family="Segoe UI", size=12)
        self.timestamp_font = font.Font(family="Segoe UI", size=8)
        
        self.setup_ui()
        self.setup_server()
        self.root.after(100, self.process_messages)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.root.title("Telegram-Style Chat Server")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS["background"])
        
        # ناحیه چت
        self.chat_frame = Frame(self.root, bg=COLORS["background"])
        self.chat_frame.pack(expand=True, fill=BOTH, padx=20, pady=10)
        
        # اسکرول بار
        scrollbar = Scrollbar(self.chat_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # کانواس برای نمایش پیام‌ها
        self.canvas = Canvas(
            self.chat_frame,
            bg=COLORS["background"],
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)
        scrollbar.config(command=self.canvas.yview)
        
        # فریم داخلی برای پیام‌ها
        self.inner_frame = Frame(self.canvas, bg=COLORS["background"])
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=NW)
        
        # ناحیه ورود پیام
        input_frame = Frame(self.root, bg=COLORS["input_bg"], height=60)
        input_frame.pack(fill=X, padx=20, pady=10)
        
        self.entry = Entry(
            input_frame,
            font=self.font,
            bg=COLORS["input_bg"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["text_white"],
            relief=FLAT
        )
        self.entry.pack(side=LEFT, expand=True, fill=X, padx=10)
        self.entry.bind("<Return>", self.send_message)
        
        send_btn = Button(
            input_frame,
            text="➤",
            font=("Arial", 14, "bold"),
            bg=COLORS["sent_msg"],
            fg=COLORS["text_white"],
            relief=FLAT,
            command=self.send_message
        )
        send_btn.pack(side=RIGHT, padx=10)

    def create_message_bubble(self, text, is_server=False):
        bubble_frame = Frame(self.inner_frame, bg=COLORS["background"])
        
        msg_frame = Frame(
            bubble_frame,
            bg=COLORS["sent_msg"] if is_server else COLORS["received_msg"],
            padx=12,
            pady=8
        )
        msg_frame.pack(side=LEFT if is_server else RIGHT)
        
        # متن پیام
        msg_label = Label(
            msg_frame,
            text=text,
            font=self.font,
            bg=msg_frame["bg"],
            fg=COLORS["text_white"],
            wraplength=400,
            justify=LEFT
        )
        msg_label.pack(anchor=W)
        
        # زمان ارسال
        timestamp = datetime.now().strftime("%H:%M")
        time_label = Label(
            msg_frame,
            text=timestamp,
            font=self.timestamp_font,
            bg=msg_frame["bg"],
            fg=COLORS["timestamp"]
        )
        time_label.pack(anchor=E)
        
        bubble_frame.pack(fill=X, pady=5)
        self.update_scroll()

    def update_scroll(self):
        self.inner_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    def send_message(self, event=None):
        text = self.entry.get().strip()
        if text:
            self.create_message_bubble(text, is_server=True)
            self.broadcast(text)
            self.entry.delete(0, END)

    def process_messages(self):
        while not self.message_queue.empty():
            msg = self.message_queue.get()
            if msg.startswith("CLIENT_MSG:"):
                _, text = msg.split(":", 1)
                self.create_message_bubble(text, is_server=False)
            elif msg.startswith("SYSTEM:"):
                _, text = msg.split(":", 1)
                self.create_system_message(text)
        self.root.after(50, self.process_messages)

    def create_system_message(self, text):
        system_frame = Frame(self.inner_frame, bg=COLORS["background"])
        label = Label(
            system_frame,
            text=text,
            font=self.timestamp_font,
            fg=COLORS["timestamp"],
            bg=COLORS["background"]
        )
        label.pack(pady=5)
        system_frame.pack(fill=X)
        self.update_scroll()

    def setup_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("localhost", 12345))
        self.server.listen(4)
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                self.connections.append(conn)
                self.message_queue.put(f"SYSTEM:New connection from {addr[0]}")
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
            except Exception as e:
                if self.running:
                    self.message_queue.put(f"SYSTEM:Server error: {str(e)}")
                break

    def handle_client(self, conn):
        while self.running:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                self.message_queue.put(f"CLIENT_MSG:{data}")
                self.broadcast(data, conn)
            except:
                break
        conn.close()
        if conn in self.connections:
            self.connections.remove(conn)

    def broadcast(self, message, sender_conn=None):
        for conn in self.connections[:]:
            if conn != sender_conn:
                try:
                    conn.send(message.encode())
                except:
                    self.connections.remove(conn)

    def on_closing(self):
        self.running = False
        for conn in self.connections:
            conn.close()
        self.server.close()
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = TelegramStyleChat(root)
    root.mainloop()