"""
第一个 AI 程序：调用 DeepSeek 大模型
前置：
  1. 在 https://platform.deepseek.com 注册并创建 API key
  2. 在本文件夹创建 .env 文件，写入：DEEPSEEK_API_KEY=sk-你的真实key
  3. 运行：pip install requests python-dotenv
"""
import os
from dotenv import load_dotenv
import requests

# 1. 从 .env 读取 key（永远不要把 key 直接写进代码！）
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 没找到 DEEPSEEK_API_KEY，请先在 .env 文件里配置")
    exit(1)

# 2. 准备请求
url = "https://api.deepseek.com/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "用一句话介绍你自己"}
    ],
}

# 3. 发送请求（带超时和错误处理）
print("正在问 DeepSeek...")
try:
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ 请求出错：{e}")
    print("常见原因：API key 不对 / 没有网络 / .env 没配置")
    exit(1)

# 4. 解析响应
result = resp.json()
answer = result["choices"][0]["message"]["content"]
print("\nDeepSeek 说：")
print(answer)
