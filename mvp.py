import os
import base64
import time
import cv2
import numpy as np
import mss
import pygetwindow as gw
import pyautogui
import pyperclip
import requests  # 新增：用于调用 AgentHub API
from openai import OpenAI

# --- 1. 配置中心 ---
CONFIG = {
    "QWEN_API_KEY": "",
    "QWEN_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "QWEN_MODEL": "qwen-vl-plus",
    
    # AgentHub 配置
    "AGENTHUB_API_URL": "https://agenthub.vongcloud.com/api/v1/chat/completions", # 请根据实际 API 路径修改
    "AGENTHUB_API_KEY": "你的_AGENTHUB_API_KEY", # ⬅️ 请在此处填写你的 AgentHub 密钥
    
    "TARGET_TITLE": "古井贡酒类旗舰店:高志-接待中心",
    "SAVE_DIR": "chat_history_steps",
    "INPUT_POS": (578, 1261),       # 来自 position_d.py
    "SEND_BUTTON_POS": (1742, 1484) # 来自 position_d.py
}

qwen_client = OpenAI(api_key=CONFIG["QWEN_API_KEY"], base_url=CONFIG["QWEN_BASE_URL"])

# --- 2. 自动化采集模块 (来自 roll.py) ---
def capture_and_scroll():
    if not os.path.exists(CONFIG["SAVE_DIR"]):
        os.makedirs(CONFIG["SAVE_DIR"])

    try:
        win = gw.getWindowsWithTitle(CONFIG["TARGET_TITLE"])[0]
        if win.isMinimized: win.restore()
        win.activate()
        # 激活焦点
        pyautogui.click(win.left + int(win.width * 0.45), win.top + int(win.height * 0.5))
        time.sleep(0.1)
    except:
        print("❌ 找不到千牛窗口。")
        return []

    monitor = {
        "left": win.left + int(win.width * 0.28),
        "top": win.top + int(win.height * 0.25),
        "width": int(win.width * 0.30),
        "height": int(win.height * 0.50)
    }
    
    image_paths = []
    with mss.mss() as sct:
        print("🚀 正在置顶聊天记录...")
        for _ in range(15): 
            pyautogui.scroll(5000) 
            time.sleep(0.01) 
        
        print("⬇️ 开始向下捕获序列...")
        count = 1
        prev_frame = None
        while count <= 3: # 采集3张足够理解上下文
            curr_frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
            if prev_frame is not None:
                res = cv2.matchTemplate(curr_frame, prev_frame, cv2.TM_CCOEFF_NORMED)
                if cv2.minMaxLoc(res)[1] > 0.999: break
            
            file_path = os.path.join(CONFIG["SAVE_DIR"], f"chat_p{count:03d}.png")
            cv2.imwrite(file_path, curr_frame)
            image_paths.append(file_path)
            prev_frame = curr_frame.copy()
            pyautogui.scroll(-600) 
            time.sleep(0.5) 
            count += 1
    return image_paths

# --- 3. 视觉整理模块 (使用 Qwen2.5 提取对话) ---
def extract_chat_context(image_paths):
    if not image_paths: return None
    
    content_list = [{"type": "text", "text": "请提取截图中的对话内容，整理成一段纯文本聊天记录，包括说话人和内容，不需要你回复，只需要整理文字。"}]
    for path in image_paths:
        with open(path, "rb") as f:
            base64_str = base64.b64encode(f.read()).decode('utf-8')
            content_list.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_str}"}
            })

    print("👁️ Qwen 正在整理视觉信息...")
    try:
        response = qwen_client.chat.completions.create(
            model=CONFIG["QWEN_MODEL"],
            messages=[{"role": "user", "content": content_list}],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Qwen 提取失败: {e}")
        return None

# --- 4. 逻辑大脑模块 (调用 AgentHub API) ---
def get_agenthub_answer(context_text):
    """将 Qwen 整理好的文本发送给 AgentHub 获取专业回复"""
    print("🧠 正在请求 AgentHub 决策...")
    headers = {
        "Authorization": f"Bearer {CONFIG['AGENTHUB_API_KEY']}",
        "Content-Type": "application/json"
    }
    # 注意：payload 结构需根据 agenthub 实际文档微调
    payload = {
        "model": "gpt-4o", # 或者 AgentHub 指定的模型名
        "messages": [
            {"role": "system", "content": "你是一个专业的古井贡酒客服，请根据提供的聊天记录给客户一个回复。"},
            {"role": "user", "content": context_text}
        ]
    }
    
    try:
        response = requests.post(CONFIG["AGENTHUB_API_URL"], headers=headers, json=payload)
        result = response.json()
        # 假设返回结构遵循 OpenAI 标准
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ AgentHub 请求错误: {e}")
        return None

# --- 5. 动作执行模块 (模拟键鼠) ---
def perform_reply_action(answer_text):
    if not answer_text: return
    
    print(f"📡 准备模拟键鼠输出内容: {answer_text}")
    # 定位到千牛输入框
    pyautogui.click(CONFIG["INPUT_POS"])
    time.sleep(0.5)
    
    # 模拟输入内容
    pyperclip.copy(answer_text) 
    pyautogui.hotkey('ctrl', 'v') 
    time.sleep(0.5)
    
    # 模拟点击发送
    pyautogui.click(CONFIG["SEND_BUTTON_POS"])
    print("✅ 任务完成，已成功回复客户。")

# --- 主程序 ---
if __name__ == "__main__":
    # 1. 采集图片
    imgs = capture_and_scroll()
    
    if imgs:
        # 2. Qwen 视觉转文字
        chat_history = extract_chat_context(imgs)
        
        if chat_history:
            # 3. AgentHub 处理逻辑
            final_answer = get_agenthub_answer(chat_history)
            
            # 4. 模拟键鼠输出
            perform_reply_action(final_answer)