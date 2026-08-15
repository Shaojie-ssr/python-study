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
    {"role": "user", "content": "用三句话介绍 Python 为什么适合新手。"},
]

data = {
    "model": "deepseek-chat",
    "messages": messages,
    "stream": True,          # ← 关键开关：开启流式
}

print("DeepSeek：", end="", flush=True)

# stream=True 时必须用 with，保证连接用完关掉
with requests.post(url, headers=headers, json=data, stream=True) as r:
    r.raise_for_status()
    for line in r.iter_lines():              # 一行一行收（SSE 一行一条）
        if not line:
            continue
        line = line.decode("utf-8")
        if not line.startswith("data:"):     # 跳过不是数据的行
            continue
        data_str = line[len("data:"):].strip()
        if data_str == "[DONE]":            # AI 发完的标志
            break
        chunk = json.loads(data_str)         # 把这一小块 JSON 解开
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:               # 这一小块里新增的文字
            print(delta["content"], end="", flush=True)  # 不换行 + 立即显示

print()  # 最后补个换行
