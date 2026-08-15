import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 DEEPSEEK_API_KEY，请先在 .env 配置并 Ctrl+S 保存")
    exit()

url = "https://api.deepseek.com/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# ---------- 1. 先写好"工具函数"（真正干活的 Python 代码）----------
def get_sales_summary(file_path: str) -> str:
    """读取销售 Excel，返回总额、总利润、最好/最差月份。"""
    df = pd.read_excel(file_path)
    total_sales = df["销售额"].sum()
    total_profit = df["利润"].sum()
    best = df.loc[df["销售额"].idxmax()]
    worst = df.loc[df["销售额"].idxmin()]
    return (f"总销售额={total_sales}，总利润={total_profit}；"
            f"最好月份={best['月份']}({best['销售额']})，"
            f"最差月份={worst['月份']}({worst['销售额']})")

def calc_diff(file_path: str) -> str:
    """计算最好月份与最差月份的销售额差值。"""
    df = pd.read_excel(file_path)
    best = df["销售额"].max()
    worst = df["销售额"].min()
    return f"最好与最差月份销售额相差 {best - worst}"

# ---------- 2. 把工具"告诉"AI（用 JSON 描述长什么样）----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_summary",
            "description": "读取销售数据 Excel 文件，返回总销售额、总利润、最好和最差月份",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Excel 文件路径，例如 sales_data.xlsx"}
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_diff",
            "description": "计算销售数据中最好月份与最差月份的销售额差值",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Excel 文件路径"}
                },
                "required": ["file_path"],
            },
        },
    },
]

# 本地函数映射：AI 说名字，我们才知道调哪个
available = {"get_sales_summary": get_sales_summary, "calc_diff": calc_diff}

# ---------- 3. 开始对话（AI 自己决定调哪个工具）----------
messages = [
    {"role": "system", "content": "你是一个数据助手，需要数据时请调用提供的工具，然后用中文简洁回答。"},
    {"role": "user", "content": "我这份销售数据（sales_data.xlsx）里，最好和最差的月份差了多少钱？"},
]

print("🤖 开始调用...\n")
for _ in range(5):  # 最多 5 轮，防止死循环
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
    }
    r = requests.post(url, headers=headers, json=data)
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]

    # AI 没要调工具 → 直接给答案，结束
    if not msg.get("tool_calls"):
        print("DeepSeek：", msg["content"])
        break

    # AI 要调工具 → 把它的"意图"原样加回对话
    messages.append(msg)

    # 逐个执行它要求的工具
    for call in msg["tool_calls"]:
        fn_name = call["function"]["name"]
        fn_args = json.loads(call["function"]["arguments"])
        print(f"🔧 AI 调用工具：{fn_name}({fn_args})")
        result = available[fn_name](**fn_args)   # 真正执行 Python 函数
        print(f"   工具返回：{result}\n")
        # 把执行结果塞回对话，让 AI 接着用
        messages.append({
            "role": "tool",
            "tool_call_id": call["id"],
            "content": result,
        })
