import os
import time
import requests
import pandas as pd
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
out = Path("summaries")
out.mkdir(exist_ok=True)

rows = []          # 用来汇总成 Excel
files = list(docs.glob("*.txt"))
print(f"📁 找到 {len(files)} 份文件，开始批量处理...\n")

for f in files:
    content = f.read_text(encoding="utf-8")      # ① 读文件
    prompt = f"""请总结以下客户反馈的要点，格式严格如下（不要多余的话）：
情绪：正面/负面/中性
要点：（一句话，不超过40字）

反馈内容：
{content}"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个严谨的客服分析助手。"},
            {"role": "user", "content": prompt},
        ],
    }

    try:                                        # ② 容错：一个坏了不影响整批
        r = requests.post(url, headers=headers, json=data, timeout=30)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]

        # ③ 每份摘要单独存一个 txt
        (out / f"{f.stem}_摘要.txt").write_text(reply, encoding="utf-8")
        rows.append({"文件": f.name, "AI摘要": reply})
        print(f"✅ {f.name} 处理完成")
    except Exception as e:
        print(f"❌ {f.name} 失败：{e}")
        rows.append({"文件": f.name, "AI摘要": f"处理失败：{e}"})

    time.sleep(1)     # ④ 每处理一个歇1秒，防 API 限流

# ⑤ 汇总成 Excel（你第 17 节学的）
df = pd.DataFrame(rows)
df.to_excel("批量摘要.xlsx", index=False)
print(f"\n🎉 全部完成！摘要在 summaries/ 文件夹，汇总表：批量摘要.xlsx")
