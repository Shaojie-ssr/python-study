import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 DEEPSEEK_API_KEY，请先在 .env 配置并 Ctrl+S 保存")
    exit()

url = "https://api.deepseek.com/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

messages = [
    {"role": "system", "content": "你是一个友好的中文助手，回答简洁、口语化。"},
]

print("👋 和 DeepSeek 聊天吧！输入「退出」结束\n")


def ask_stream(user_text):
    """用户说一句，AI 流式回复并打印。"""
    messages.append({"role": "user", "content": user_text})
    data = {"model": "deepseek-chat", "messages": messages, "stream": True}
    print("DeepSeek：", end="", flush=True)
    reply_parts = []
    with requests.post(url, headers=headers, json=data, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data:"):
                continue
            data_str = line[len("data:"):].strip()
            if data_str == "[DONE]":
                break
            chunk = json.loads(data_str)
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                print(delta["content"], end="", flush=True)
                reply_parts.append(delta["content"])
    print("\n")
    messages.append({"role": "assistant", "content": "".join(reply_parts)})


while True:
    user_input = input("你：")
    if user_input == "退出":
        print("👋 拜拜！")
        break
    ask_stream(user_input)
