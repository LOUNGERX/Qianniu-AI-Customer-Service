import pyautogui
import time

print("开始坐标探测，请在 3 秒内将鼠标挪到【输入框】中心...")
time.sleep(3)
input_pos = pyautogui.position()
print(f"✅ 记录到输入框坐标: {input_pos}")

print("请在 3 秒内将鼠标挪到【发送按钮】中心...")
time.sleep(3)
send_pos = pyautogui.position()
print(f"✅ 记录到发送按钮坐标: {send_pos}")