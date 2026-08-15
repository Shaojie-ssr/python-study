import requests
import os
from dotenv import load_dotenv

# 1. 读 key（和上一节一样）
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

# 2. 对话历史：先放一个 system 角色（给 AI 定人设）
messages = [
    {"role": "system", "content": "你是一个友好的中文助手，回答简洁、口语化。"},
]

print("👋 和 DeepSeek 聊天吧！输入「退出」结束\n")

# 3. 无限循环，一直聊
while True:
    user_input = input("你：")
    if user_input == "退出":
        print("👋 拜拜！")
        break

    # 4. 把你说的话加进历史
    messages.append({"role": "user", "content": user_input})

    # 5. 把【整段历史】一起发给 API
    data = {"model": "deepseek-chat", "messages": messages}
    try:
        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ 出错了：{e}")
        continue

    # 6. 把 AI 的回复也加进历史（关键！下一轮它才"记得"）
    messages.append({"role": "assistant", "content": reply})
    print(f"DeepSeek：{reply}\n")
