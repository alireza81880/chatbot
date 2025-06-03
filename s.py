import subprocess
import re
import ctypes
import sys

def is_admin():
    """بررسی دسترسی ادمین"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_wifi_passwords():
    try:
        # دریافت لیست شبکه‌ها با encoding مناسب
        profiles_output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'], 
            encoding='cp1252',
            errors='replace'
        ).split('\n')
        
        # استخراج نام شبکه‌ها (برای سیستم‌های انگلیسی)
        profiles = [
            line.split(':')[1].strip() 
            for line in profiles_output 
            if "All User Profile" in line
        ]

        # استخراج رمزهای عبور
        results = []
        for profile in profiles:
            try:
                profile_info = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], 
                    encoding='cp1252',
                    errors='replace'
                )
                password_match = re.search(r'Key Content\s*:\s*(.*)', profile_info)
                password = password_match.group(1).strip() if password_match else 'یافت نشد'
                results.append(f'شبکه: {profile}\nرمز عبور: {password}\n{"-"*40}')
            except Exception as e:
                results.append(f'شبکه: {profile}\nخطا: {str(e)}\n{"-"*40}')

        return '\n'.join(results) if results else 'هیچ شبکه وایفای ذخیره شده‌ای یافت نشد'
    
    except Exception as e:
        return f'خطا: {str(e)}'

if __name__ == '__main__':
    if not is_admin():
        print("این اسکریپت نیاز به دسترسی Administrator دارد!")
        print("لطفا با راست کلیک -> Run as Administrator اجرا کنید.")
        sys.exit(1)
        
    print('در حال دریافت رمزهای وایفای...\n')
    wifi_info = get_wifi_passwords()
    print(wifi_info)