"""AI 自动整理客户邮件 —— 读 emails/ 文件夹，批量分类，输出摘要 + 总表。

运行：
    1. python make_sample_emails.py   # 先造 10 封示例邮件
    2. python organize_emails.py      # AI 自动整理

配置（想换模型/换云端，改下面这段就行）：
"""
# ===================== 配置区 =====================
USE_LOCAL = True          # True=本地 Ollama（免费/离线）；False=云端 DeepSeek
LOCAL_URL = "http://localhost:11434/v1/chat/completions"
LOCAL_MODEL = "deepseek-r1:7b"      # 本地模型名（换成 qwen2.5:7b 也行）
CLOUD_URL = "https://api.deepseek.com/chat/completions"
CLOUD_MODEL = "deepseek-chat"
# =================================================

import os
import re
import json
import time
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# —— 选云端时读 key；本地用占位符 ——
load_dotenv()
if USE_LOCAL:
    url = LOCAL_URL
    model = LOCAL_MODEL
    headers = {"Authorization": "Bearer ollama", "Content-Type": "application/json"}
else:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY，请先在 .env 配置并 Ctrl+S 保存")
        exit()
    url = CLOUD_URL
    model = CLOUD_MODEL
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

emails_dir = Path("emails")
out_dir = Path("邮件整理结果")
out_dir.mkdir(exist_ok=True)

files = list(emails_dir.glob("*.txt"))
if not files:
    print("⚠️ emails/ 里没有 .txt，请先运行 python make_sample_emails.py")
    exit()

print(f"📂 找到 {len(files)} 封邮件，开始 AI 整理...\n")


def extract_json(text):
    """从模型回复里抠出 JSON（模型偶尔会用 ```json 包裹，这里兜底处理）。"""
    text = text.strip()
    # 去掉 markdown 代码块围栏
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    # 如果还裹着，找第一个 { 到最后一个 }
    if not text.startswith("{"):
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1:
            text = text[s:e + 1]
    return json.loads(text)


rows = []
for f in files:
    content = f.read_text(encoding="utf-8")
    prompt = f"""分析以下客户邮件，必须只返回一个 JSON 对象，不要任何解释、不要 markdown。
字段要求：
- "意图": 从 ["投诉","咨询","表扬","催款","续费","技术支持","合作","退订","其他"] 选一个
- "优先级": 从 ["高","中","低"] 选一个（投诉/催款/退订/技术故障=高）
- "情绪": 从 ["正面","负面","中性"] 选一个
- "需回复": true 或 false（布尔值，不需要回复的填 false）
- "摘要": 不超过 35 字的中文一句话，说清客户要啥
- "建议动作": 不超过 30 字，你作为客服主管建议下一步怎么做

邮件内容：
{content}"""

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是资深客服主管，只输出合法 JSON。"},
            {"role": "user", "content": prompt},
        ],
    }
    if USE_LOCAL:
        data["stream"] = False   # 批量处理不流式，收完再写

    try:
        r = requests.post(url, headers=headers, json=data, timeout=120)
        r.raise_for_status()
        result = r.json()["choices"][0]["message"]["content"]
        obj = extract_json(result)          # 兜底解析 JSON
        obj["邮件"] = f.name
        rows.append(obj)

        # 每封单独存一个摘要文件
        summary = (
            f"【{f.name}】\n"
            f"意图：{obj['意图']}  |  优先级：{obj['优先级']}  |  情绪：{obj['情绪']}\n"
            f"需回复：{'是' if obj['需回复'] else '否'}\n"
            f"摘要：{obj['摘要']}\n"
            f"建议动作：{obj['建议动作']}\n"
        )
        (out_dir / f"{f.stem}_整理.txt").write_text(summary, encoding="utf-8")
        print(f"✅ {f.name}：{obj['意图']}/{obj['优先级']}优先/{obj['情绪']}")
    except Exception as e:
        print(f"❌ {f.name} 失败：{e}")
        rows.append({"邮件": f.name, "意图": "解析失败", "优先级": "-",
                     "情绪": "-", "需回复": False, "摘要": str(e), "建议动作": "-"})

    time.sleep(1)   # 本地模型慢，歇 1 秒防卡

# 汇总成 Excel（按优先级排序：高 → 中 → 低）
df = pd.DataFrame(rows)
priority_order = {"高": 0, "中": 1, "低": 2}
df["_o"] = df["优先级"].map(priority_order).fillna(9)
df = df.sort_values("_o").drop(columns="_o")
df.to_excel(out_dir / "邮件分类总表.xlsx", index=False)

print(f"\n🎉 整理完成！")
print(f"   每封摘要：{out_dir}/ 文件夹")
print(f"   分类总表：{out_dir}/邮件分类总表.xlsx（按优先级排序）")
