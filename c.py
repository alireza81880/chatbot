import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from datetime import datetime

class TelegramStyleClient:
    def __init__(self, root):
        self.root = root
        self.root.title("تلگرام")
        self.root.geometry("400x600")
        self.root.configure(bg='#182533')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.running = True
        self.client = None
        self.username = None
        
        # رنگ‌بندی تلگرام
        self.colors = {
            'bg': '#182533',
            'msg_sent': '#2b5278',
            'msg_received': '#2d4369',
            'text': '#ffffff',
            'time': '#a8b8c8',
            'input_bg': '#2a3f5a',
            'error': '#5c2b29'
        }
        
        self.setup_ui()
        self.connect_to_server()

    def setup_ui(self):
        """تنظیم رابط کاربری گرافیکی"""
        # ناحیه چت
        self.chat_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.chat_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # کانواس و اسکرول بار
        self.canvas = tk.Canvas(
            self.chat_frame,
            bg=self.colors['bg'],
            highlightthickness=0,
            yscrollincrement=5
        )
        scrollbar = tk.Scrollbar(self.chat_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # ناحیه ورود پیام
        input_frame = tk.Frame(self.root, bg=self.colors['input_bg'], height=60)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.entry = tk.Entry(
            input_frame,
            font=('Segoe UI', 12),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry.bind("<Return>", self.send_message)
        
        self.send_btn = tk.Button(
            input_frame,
            text="➤",
            font=('Arial', 14, 'bold'),
            bg=self.colors['msg_sent'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            command=self.send_message
        )
        self.send_btn.pack(side=tk.RIGHT, padx=5)

    def connect_to_server(self):
        """اتصال به سرور"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(('localhost', 12345))
            
            # دریافت نام کاربری
            self.get_username()
            
            # شروع دریافت پیام‌ها
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
        except ConnectionRefusedError:
            self.show_error("سرور در دسترس نیست")
            self.root.after(2000, self.root.destroy)
        except Exception as e:
            self.show_error(f"خطا در اتصال: {str(e)}")
            self.root.after(2000, self.root.destroy)

    def get_username(self):
        """دریافت نام کاربری از کاربر"""
        while True:
            username = simpledialog.askstring(
                "نام کاربری",
                "لطفاً نام کاربری خود را وارد کنید:",
                parent=self.root
            )
            
            if username:
                self.username = username
                try:
                    self.client.send(username.encode('utf-8'))
                    break
                except:
                    self.show_error("خطا در ارسال نام کاربری")
                    self.root.destroy()
                    break
            else:
                if not messagebox.askretrycancel("توجه", "نام کاربری نمی‌تواند خالی باشد"):
                    self.root.destroy()
                    break

    def receive_messages(self):
        """دریافت پیام‌ها از سرور"""
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if not message:
                    self.show_error("ارتباط با سرور قطع شد")
                    break
                    
                self.add_message(message, "received")
                
            except ConnectionResetError:
                if self.running:
                    self.show_error("ارتباط با سرور قطع شد")
                break
            except Exception as e:
                if self.running:
                    self.show_error(f"خطا در دریافت پیام: {str(e)}")
                break

    def send_message(self, event=None):
        """ارسال پیام به سرور"""
        message = self.entry.get().strip()
        if message:
            self.entry.delete(0, tk.END)
            try:
                self.client.send(message.encode('utf-8'))
                self.add_message(f"شما: {message}", "sent")
                
                if message.lower() == 'exit':
                    self.running = False
                    self.root.after(1000, self.root.destroy)
                    
            except Exception as e:
                self.show_error(f"خطا در ارسال پیام: {str(e)}")

    def add_message(self, message, msg_type):
        """نمایش پیام در ناحیه چت"""
        frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg'])
        
        if msg_type == "sent":
            bg = self.colors['msg_sent']
            side = "right"
        elif msg_type == "received":
            bg = self.colors['msg_received']
            side = "left"
        else:  # error or system
            bg = self.colors['error'] if msg_type == "error" else self.colors['bg']
            side = "left"
        
        msg_frame = tk.Frame(frame, bg=bg, padx=10, pady=5)
        tk.Label(
            msg_frame,
            text=message,
            bg=bg,
            fg=self.colors['text'],
            font=('Segoe UI', 11),
            wraplength=300,
            justify='left'
        ).pack(anchor='w')
        
        if msg_type in ("sent", "received"):
            tk.Label(
                msg_frame,
                text=datetime.now().strftime("%H:%M"),
                bg=bg,
                fg=self.colors['time'],
                font=('Segoe UI', 8)
            ).pack(anchor='e')
        
        msg_frame.pack(side=side, fill=tk.X, padx=5, pady=2)
        frame.pack(fill=tk.X)
        
        self.update_scroll()

    def update_scroll(self):
        """به‌روزرسانی اسکرول"""
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    def show_error(self, message):
        """نمایش پیام خطا"""
        self.add_message(message, "error")
        messagebox.showerror("خطا", message)

    def on_closing(self):
        """مدیریت رویداد بسته شدن پنجره"""
        if self.running:
            if messagebox.askokcancel("خروج", "آیا مطمئنید می‌خواهید خارج شوید؟"):
                self.running = False
                try:
                    self.client.send('exit'.encode('utf-8'))
                except:
                    pass
                finally:
                    if self.client:
                        self.client.close()
                    self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = TelegramStyleClient(root)
    root.mainloop()