import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 DEEPSEEK_API_KEY，请先配置并 Ctrl+S 保存")
    exit()

url = "https://api.deepseek.com/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# ---------- 1. 建知识库（切分 = 每段一个 chunk）----------
KNOWLEDGE = Path("kb")
def build_chunks():
    chunks = []
    for f in KNOWLEDGE.glob("*.txt"):
        text = f.read_text(encoding="utf-8")
        for para in text.split("\n\n"):     # 按空行切段
            para = para.strip()
            if para:
                chunks.append({"source": f.name, "text": para})
    return chunks

# ---------- 2. 检索（中文用"相邻两字"做关键词）----------
def tokenize(text):
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+", text)              # 英文/数字
    chinese = re.findall(r"[\u4e00-\u9fff]+", text)       # 中文整词
    bigrams = []
    for w in chinese:
        bigrams += [w[i] + w[i+1] for i in range(len(w)-1)]
    return set(tokens + bigrams)

def retrieve(query, chunks, top_k=2):
    q_tokens = tokenize(query)
    scored = []
    for c in chunks:
        score = len(q_tokens & tokenize(c["text"]))      # 共有词越多越相关
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:top_k]]

chunks = build_chunks()
print(f"📚 知识库已载入 {len(chunks)} 段，开始提问（输入「退出」结束）\n")

# ---------- 3. 检索 + 增强 + 生成 ----------
def ask(q):
    hits = retrieve(q, chunks, top_k=2)
    if not hits:
        print("DeepSeek：资料里没有相关信息。\n")
        return
    context = "\n\n".join(f"[来源：{h['source']}]\n{h['text']}" for h in hits)
    prompt = f"""只根据下面的资料回答用户的问题。如果资料里没有答案，直接说"资料里没有相关信息"，不要编造。

资料：
{context}

问题：{q}"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是公司知识库助手，只依据资料回答。"},
            {"role": "user", "content": prompt},
        ],
        "stream": True,
    }
    print("DeepSeek：", end="", flush=True)
    with requests.post(url, headers=headers, json=data, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data:"):
                continue
            ds = line[5:].strip()
            if ds == "[DONE]":
                break
            chunk = json.loads(ds)
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                print(delta["content"], end="", flush=True)
    print("\n")

while True:
    q = input("你：")
    if q == "退出":
        print("👋 拜拜！")
        break
    ask(q)
