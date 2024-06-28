import ts3
from ts3.definitions import TextMessageTargetMode
from ts3.query import TS3TimeoutError
import socket
import json
import time
import random
import string
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ------------------------------- config -------------------------------
TS_QUERY_USERNAME = "USERNAME"
TS_QUERY_PASSWORD = "TS_QUERY_PASSWORD"
TS_ADDRESS = "cr7.haoyuebz.love"
BOT_DISPLAY_NAME = "Gemini BOT"
TS_CHANNEL_ID = 1
MESSAGE_PREFIX = "!BOT"
TELNET_PORT = 10011
CHAT_HISTORY_FILE = 'chat_history.json'

# 配置Google Gemini API密钥
API_KEY = "APIKEY"
genai.configure(api_key=API_KEY)

# 设置生成模型配置并调整安全设置
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 99999999,
    "response_mime_type": "text/plain",
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

chat_history = []

def load_chat_history():
    global chat_history
    try:
        with open(CHAT_HISTORY_FILE, 'r') as f:
            chat_history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        chat_history = []

def get_gemini_response(message):
    global chat_history
    chat_history.append({
        "role": "user",
        "parts": [message]
    })
    
    response = model.start_chat(
        history=chat_history
    ).send_message(message)

    if response:
        print(f"生成的响应: {response.text}")
    else:
        print("抱歉，我无法处理您的请求。")

    response_text = response.text if response else "抱歉，我无法处理您的请求。"
    
    chat_history.append({
        "role": "model",
        "parts": [response_text]
    })
    
    return response_text

def is_port_open(host, port, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

def ts_chat_bot(ts3conn):
    global chat_history, waiting_for_password, password_attempts
    waiting_for_password = False
    password_attempts = 0
    PASSWORD = "password"
    MAX_ATTEMPTS = 3

    print("已连接到TeamSpeak服务器并开始监听消息...")
    ts3conn.exec_("clientupdate", client_nickname=BOT_DISPLAY_NAME)
    own_client_id = ts3conn.exec_("whoami")[0]['client_id']
    current_channel_id = ts3conn.exec_("clientinfo", clid=own_client_id)[0]['cid']
    
    if current_channel_id != str(TS_CHANNEL_ID):
        ts3conn.exec_("clientmove", clid=own_client_id, cid=TS_CHANNEL_ID)

    ts3conn.exec_("servernotifyregister", event="textchannel")

    while True:
        ts3conn.send_keepalive()
        try:
            event = ts3conn.wait_for_event(timeout=120)
        except TS3TimeoutError:
            continue

        if event[0]["invokerid"] != own_client_id:
            message = event[0]["msg"].strip()
            if message.lower() == "!reset":
                waiting_for_password = True
                ts3conn.exec_("sendtextmessage", targetmode=TextMessageTargetMode.CHANNEL, msg="输入密码重置BOT")
                continue

            if waiting_for_password:
                if message == PASSWORD:
                    load_chat_history()  # 重新加载历史，但不修改文件
                    ts3conn.exec_("sendtextmessage", targetmode=TextMessageTargetMode.CHANNEL, msg="已重置BOT")
                    waiting_for_password = False
                    password_attempts = 0
                else:
                    password_attempts += 1
                    if password_attempts >= MAX_ATTEMPTS:
                        ts3conn.exec_("sendtextmessage", targetmode=TextMessageTargetMode.CHANNEL, msg="失败")
                        waiting_for_password = False
                        password_attempts = 0
                    else:
                        ts3conn.exec_("sendtextmessage", targetmode=TextMessageTargetMode.CHANNEL, msg=f"密码错误!! 还有{MAX_ATTEMPTS - password_attempts}次机会。")
                continue

            if message.lower().startswith(MESSAGE_PREFIX.lower()):
                message_content = message[len(MESSAGE_PREFIX):].strip()
                response = get_gemini_response(message_content)
                print(f"输入: {message_content}")
                print(f"输出: {response}")
                ts3conn.exec_("sendtextmessage", targetmode=TextMessageTargetMode.CHANNEL, msg=response)

def generate_unique_nickname(base_name):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_name}_{suffix}"

def connect_to_ts():
    unique_nickname = generate_unique_nickname(BOT_DISPLAY_NAME)
    while True:
        if not is_port_open(TS_ADDRESS, TELNET_PORT):
            print(f"无法连接到 {TS_ADDRESS} 的端口 {TELNET_PORT}。请检查服务器和网络设置。")
            time.sleep(10)  # 等待一段时间后重试
            continue

        try:
            with ts3.query.TS3ServerConnection(f"telnet://{TS_QUERY_USERNAME}:{TS_QUERY_PASSWORD}@{TS_ADDRESS}:{TELNET_PORT}") as ts3conn:
                ts3conn.exec_("use", sid=1)
                ts3conn.exec_("clientupdate", client_nickname=unique_nickname)
                ts_chat_bot(ts3conn)
        except Exception as e:
            print(f"连接失败，尝试重新连接: {e}")
            time.sleep(10)  # 等待一段时间后重试

if __name__ == "__main__":
    load_chat_history()  # 初次加载历史记录
    connect_to_ts()  # 连接或重连不再重新加载历史记录
