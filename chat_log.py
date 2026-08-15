import os
import json
import requests
from dotenv import load_dotenv

LOG_FILE = "chat_log.json"
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 DEEPSEEK_API_KEY，请先在 .env 配置并 Ctrl+S 保存")
    exit()

url = "https://api.deepseek.com/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# ① 启动时：尝试读回历史对话
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)
    print(f"📂 已载入 {len(messages) - 1} 条历史对话（上次聊的都在）\n")
else:
    messages = [
        {"role": "system", "content": "你是一个友好的中文助手，回答简洁、口语化。"},
    ]
    print("👋 第一次聊天，开始新对话\n")

print("输入「退出」结束（对话会自动保存）\n")


def ask_stream(user_text):
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

    # ② 每轮结束后立刻写盘（即使中途关掉也不丢）
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print("💾 已保存到 chat_log.json\n")


while True:
    user_input = input("你：")
    if user_input == "退出":
        print("👋 拜拜！（历史已保存）")
        break
    ask_stream(user_input)
