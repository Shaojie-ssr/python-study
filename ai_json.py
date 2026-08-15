import os
import json
import time
import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # 后台画图，不弹窗口（服务器/无界面必备）
import matplotlib.pyplot as plt
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 DEEPSEEK_API_KEY，请先在 .env 配置并 Ctrl+S 保存")
    exit()

url = "https://api.deepseek.com/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

docs = Path("docs")
rows = []
print(f"📁 读取反馈，让 AI 输出 JSON...\n")

for f in docs.glob("*.txt"):
    content = f.read_text(encoding="utf-8")
    prompt = f"""分析以下客户反馈，必须只返回一个 JSON 对象，不要任何解释、不要 markdown 代码块。
字段如下：
- "情绪": 只能是 "正面" / "负面" / "中性"
- "类别": 从 ["性能","价格","客服","界面","其他"] 选一个
- "评分": 1 到 5 的整数（5 最好）
- "要点": 不超过 30 字的中文一句话

反馈内容：
{content}"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你只输出合法的 JSON，不要冗余文字。"},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},   # ① 强制 AI 输出 JSON
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        r.raise_for_status()
        result = r.json()["choices"][0]["message"]["content"]  # ② 这就是 JSON 字符串
        obj = json.loads(result)                             # ③ 秒变 dict
        obj["文件"] = f.name
        rows.append(obj)
        print(f"✅ {f.name}：{obj['情绪']} / {obj['类别']} / {obj['评分']}★")
    except Exception as e:
        print(f"❌ {f.name} 失败：{e}")

    time.sleep(1)

# ④ 把 AI 的 JSON 直接变成 DataFrame（你第 17 节学的）
df = pd.DataFrame(rows)
print("\n📊 汇总表：")
print(df[["文件", "情绪", "类别", "评分", "要点"]].to_string(index=False))

# ⑤ 用 JSON 结果画图（你第 17 节学的 matplotlib）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]   # 中文不乱码
plt.rcParams["axes.unicode_minus"] = False

# 饼图：情绪分布
counts = df["情绪"].value_counts()
plt.figure(figsize=(5, 5))
plt.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=90)
plt.title("客户反馈情绪分布")
plt.savefig("情绪分布.png", dpi=120, bbox_inches="tight")
plt.close()

# 条形图：各反馈评分
plt.figure(figsize=(7, 4))
plt.bar(df["文件"].str.replace(".txt", ""), df["评分"], color="#4C72B0")
plt.ylim(0, 5)
plt.ylabel("评分（1-5）")
plt.title("各反馈评分")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("评分图.png", dpi=120, bbox_inches="tight")
plt.close()

print("\n🎉 已生成 情绪分布.png 和 评分图.png")
