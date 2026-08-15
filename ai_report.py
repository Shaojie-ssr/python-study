import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

# 1. 准备数据：没有 Excel 就自动造一个示例
if not os.path.exists("sales_data.xlsx"):
    print("没找到 sales_data.xlsx，自动造一个示例...")
    data = {
        "月份": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "销售员": ["张三", "李四", "王五", "张三", "李四", "王五"],
        "销售额": [12000, 15000, 9000, 18000, 16000, 21000],
        "利润": [3000, 4200, 2100, 5400, 4800, 6300],
    }
    pd.DataFrame(data).to_excel("sales_data.xlsx", index=False)
    print("已生成 sales_data.xlsx")

# 2. 用 pandas 读 Excel，转成 AI 能读的纯文本
df = pd.read_excel("sales_data.xlsx")
data_text = df.to_string(index=False)

# 3. 拼 prompt：给 AI 分析师角色 + 数据 + 要求
prompt = f"""你是一名资深销售分析师。以下是公司的月度销售数据：

{data_text}

请写一段 250 字以内的中文分析报告，包含：
1. 总销售额和总利润
2. 表现最好和最差的月份
3. 一个可落地的改进建议
用清晰的分点，不要代码。"""

# 4. 调 DeepSeek（复用你第 3 节的流式逻辑）
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 DEEPSEEK_API_KEY，请先在 .env 配置并 Ctrl+S 保存")
    exit()

url = "https://api.deepseek.com/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
messages = [
    {"role": "system", "content": "你是一名严谨的中文销售分析师，报告简洁、有数据支撑。"},
    {"role": "user", "content": prompt},
]
data = {"model": "deepseek-chat", "messages": messages, "stream": True}

print("\n📊 AI 正在分析报告...\n")
report_parts = []
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
            report_parts.append(delta["content"])
print("\n")

# 5. 把报告存盘（你第 12 节学的文件读写）
report = "".join(report_parts)
with open("ai_report.txt", "w", encoding="utf-8") as f:
    f.write("AI 销售分析报告\n")
    f.write("=" * 30 + "\n\n")
    f.write(report)
print("✅ 报告已保存到 ai_report.txt，用记事本打开看看")
