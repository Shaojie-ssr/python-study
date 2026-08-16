"""
阶段2 第4课：requests 调用 API
===============================
API（Application Programming Interface，应用程序接口）
就是「程序之间的对话方式」。

本课学什么：
  1. HTTP 基础：GET/POST/PUT/DELETE
  2. HTTP 状态码：200/404/500 是什么意思
  3. requests 库发请求
  4. 解析 JSON 响应
  5. 带参数的 GET 请求
  6. POST 请求和请求体
  7. 请求头 Headers、API Key 鉴权
  8. 错误处理：timeout、连接失败
  9. 把 API 数据保存到 CSV

运行方式：python lesson9_requests_api.py
"""

import requests
import json
import pandas as pd
from datetime import datetime

print("=" * 70)
print("阶段2 第4课：requests 调用 API")
print("=" * 70)


# ──────────────────────────────────────────────
# 0. HTTP 基础速览
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("0. HTTP 基础速览")
print("─" * 70)
print("""
HTTP 方法：
  GET     获取数据（查）
  POST    提交数据（增）
  PUT     更新数据（改）
  DELETE  删除数据（删）

常见状态码：
  200 OK            成功
  201 Created       创建成功
  400 Bad Request   请求参数错误
  401 Unauthorized  未授权（可能没传 API Key）
  403 Forbidden     禁止访问
  404 Not Found     资源不存在
  500 Server Error  服务器内部错误
  503 Service Unavailable 服务暂时不可用
""")


# ──────────────────────────────────────────────
# 1. 最简单的 GET 请求
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("1. 最简单的 GET 请求")
print("─" * 70)

# httpbin.org 是一个测试 API，会把你发的东西原样返回
url = "https://httpbin.org/get"
try:
    response = requests.get(url, timeout=10)
    print(f"状态码：{response.status_code}")
    print(f"响应类型：{response.headers.get('Content-Type')}")
    print("\n响应内容（前 500 字符）：")
    print(response.text[:500])
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")


# ──────────────────────────────────────────────
# 2. GET 带参数
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("2. GET 带参数（params）")
print("─" * 70)

url = "https://httpbin.org/get"
params = {
    "invoice_no": "INV-2026-001",
    "currency": "USD",
    "page": 1,
    "page_size": 20,
}
try:
    response = requests.get(url, params=params, timeout=10)
    print(f"状态码：{response.status_code}")
    # 转成 JSON 字典
    data = response.json()
    print("\n请求 URL（requests 自动拼好的）：")
    print(data["url"])
    print("\n请求参数：")
    print(data["args"])
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")


# ──────────────────────────────────────────────
# 3. POST 请求
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("3. POST 请求（提交 JSON 数据）")
print("─" * 70)

url = "https://httpbin.org/post"
payload = {
    "customer_code": "KH001",
    "invoice_no": "INV-2026-001",
    "amount": 15800.00,
    "currency": "USD",
}
try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"状态码：{response.status_code}")
    data = response.json()
    print("\n提交的数据：")
    print(json.dumps(data["json"], ensure_ascii=False, indent=2))
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")


# ──────────────────────────────────────────────
# 4. 请求头 Headers
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("4. 请求头 Headers")
print("─" * 70)

url = "https://httpbin.org/headers"
headers = {
    "User-Agent": "FDE-Study-Bot/1.0",
    "Accept": "application/json",
    "X-Custom-Header": "shaojie-learning-requests",
}
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"状态码：{response.status_code}")
    print("\n服务器收到的请求头：")
    print(json.dumps(response.json()["headers"], ensure_ascii=False, indent=2))
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")


# ──────────────────────────────────────────────
# 5. 调用真实 API：免费汇率 API
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("5. 调用真实 API：免费汇率 API")
print("─" * 70)

# exchangerate-api 的免费接口，无需 API Key
exchange_url = "https://api.exchangerate-api.com/v4/latest/USD"
try:
    response = requests.get(exchange_url, timeout=15)
    print(f"状态码：{response.status_code}")

    if response.status_code == 200:
        rate_data = response.json()
        print(f"\n基准货币：{rate_data['base']}")
        print(f"汇率日期：{rate_data['date']}")

        rates = rate_data["rates"]
        print(f"\nUSD → CNY：{rates.get('CNY')}")
        print(f"USD → EUR：{rates.get('EUR')}")
        print(f"USD → JPY：{rates.get('JPY')}")
        print(f"USD → KRW：{rates.get('KRW')}")

        # 把汇率保存到 CSV
        rate_df = pd.DataFrame(
            list(rates.items()),
            columns=["currency", "rate_to_usd"]
        )
        rate_df.to_csv("data/exchange_rates.csv", index=False, encoding="utf-8-sig")
        print("\n✅ 汇率已保存到 data/exchange_rates.csv")
    else:
        print(f"请求失败，状态码：{response.status_code}")

except requests.exceptions.Timeout:
    print("请求超时，可能是网络较慢或 API 服务繁忙。")
except requests.exceptions.ConnectionError:
    print("连接失败，请检查网络或代理设置。")
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")


# ──────────────────────────────────────────────
# 6. API Key 鉴权概念（示例，不需要真实 Key）
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("6. API Key 鉴权概念")
print("─" * 70)

print("""
大多数商业 API 需要鉴权，常见两种方式：

方式一：Header 里带 API Key
  headers = {"Authorization": "Bearer YOUR_API_KEY"}
  requests.get(url, headers=headers)

方式二：URL 参数里带 API Key（不推荐，容易泄露）
  params = {"api_key": "YOUR_API_KEY"}
  requests.get(url, params=params)

重要：API Key 永远不要写死在代码里！
  ✅ 放到 .env 文件或环境变量
  ✅ .gitignore 里排除 .env
  ❌ 不要上传到 GitHub
""")

# 演示：从环境变量读取（假设你设置了 OPENAI_API_KEY）
import os
api_key = os.environ.get("OPENAI_API_KEY", "未设置")
print(f"环境变量 OPENAI_API_KEY：{api_key[:10] if api_key != '未设置' else api_key}...")
print("（这是演示，实际调用时从环境变量读，不要写死）")


# ──────────────────────────────────────────────
# 7. 封装一个健壮的 API 请求函数
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("7. 封装一个健壮的 API 请求函数")
print("─" * 70)

def fetch_exchange_rate(base="USD", timeout=10):
    """
    获取指定基准货币的最新汇率。
    成功返回汇率字典，失败返回 None。
    """
    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # 如果不是 2xx，会抛出异常
        return response.json()
    except requests.exceptions.Timeout:
        print(f"获取 {base} 汇率超时")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误：{e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常：{e}")
        return None


rate_result = fetch_exchange_rate("USD")
if rate_result:
    print(f"\n成功获取 {rate_result['base']} 汇率")
    print(f"USD → CNY：{rate_result['rates'].get('CNY')}")
    print(f"USD → EUR：{rate_result['rates'].get('EUR')}")
else:
    print("\n获取汇率失败，跳过后续计算。")


# ──────────────────────────────────────────────
# 8. 实战：用实时汇率换算发票金额
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("8. 实战：用实时汇率换算发票金额")
print("─" * 70)

# 示例发票
invoices = [
    {"invoice_no": "INV-2026-001", "currency": "USD", "amount": 15800.00},
    {"invoice_no": "INV-2026-004", "currency": "EUR", "amount": 18900.00},
    {"invoice_no": "INV-2026-006", "currency": "JPY", "amount": 2100000.00},
]

if rate_result:
    rates = rate_result["rates"]
    print("\n发票实时汇率换算：")
    for inv in invoices:
        rate = rates.get(inv["currency"])
        if rate:
            # 先把外币转成 USD，再把 USD 转成 CNY
            # 或者直接用该货币对 CNY 的汇率
            cny_rate = rates.get("CNY", 7.2)
            # 如果 API 直接有 CNY 对该货币的汇率，也可以直接用
            # 这里用 USD 作为桥梁：外币金额 / 该货币对USD汇率 * USD对CNY汇率
            usd_amount = inv["amount"] / rate
            cny_amount = usd_amount * cny_rate
            print(f"{inv['invoice_no']}: {inv['amount']} {inv['currency']} ≈ {cny_amount:,.2f} CNY")
        else:
            print(f"{inv['invoice_no']}: 未找到 {inv['currency']} 汇率")
else:
    print("由于汇率获取失败，无法演示换算。")


# ──────────────────────────────────────────────
# 总结
# ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("本课总结")
print("=" * 70)
print("""
requests 核心操作速记表：
┌──────────────────┬─────────────────────────────────────────────┐
│ 操作             │ 代码                                        │
├──────────────────┼─────────────────────────────────────────────┤
│ GET 请求         │ requests.get(url, params=..., timeout=10)   │
│ POST 请求        │ requests.post(url, json=..., timeout=10)    │
│ 加请求头         │ requests.get(url, headers=headers)          │
│ 看状态码         │ response.status_code                        │
│ 看响应文本       │ response.text                               │
│ 转 JSON 字典     │ response.json()                             │
│ 检查是否成功     │ response.raise_for_status()                 │
│ 处理超时         │ requests.exceptions.Timeout                 │
│ 处理连接错误     │ requests.exceptions.ConnectionError         │
│ 通用异常         │ requests.exceptions.RequestException        │
└──────────────────┴─────────────────────────────────────────────┘

口诀：
  GET 查、POST 增、PUT 改、DELETE 删；
  状态码看 200/404/500，超时连接要 try；
  JSON 解析 response.json()，API Key 别写死。
""")

print("✅ 阶段2 第4课完成！运行成功后截图发我，进入第5课 ETL 综合项目。")
