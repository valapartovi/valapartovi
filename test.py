import threading
import time

def print_numbers():
    for i in range(5):
        print(f"Number: {i}")
        time.sleep(1)

def print_letters():
    for letter in 'ABCDE':
        print(f"Letter: {letter}")
        time.sleep(1)

# ایجاد نخ‌ها
thread1 = threading.Thread(target=print_numbers)
thread2 = threading.Thread(target=print_letters)

# شروع نخ‌ها
thread1.start()
thread2.start()

# انتظار برای پایان نخ‌ها
thread1.join()
thread2.join()

print("All threads are done!")
