# lesson4.py - 文件读写
# 目标：学会用 open/with 读写 txt/csv，结合外贸发票场景
import csv
import os

# 确保输出目录存在
os.makedirs("D:/Python_study/output", exist_ok=True)

# ==================== 1. 写文本文件 ====================
# 场景：把一条开票记录写进日志
with open("D:/Python_study/output/invoice_log.txt", "w", encoding="utf-8") as f:
    f.write("2026-08-16 开具销售发票\n")
    f.write("报关单号：123456789\n")
    f.write("金额：10000 USD\n")

print("日志已写入")

# ==================== 2. 读文本文件 ====================
with open("D:/Python_study/output/invoice_log.txt", "r", encoding="utf-8") as f:
    content = f.read()

print("--- 文件内容 ---")
print(content)

# ==================== 3. 按行读取并处理 ====================
# 场景：读取多行发票金额，计算总和
lines = [
    "A公司,1000,USD",
    "B公司,2500,USD",
    "C公司,800,USD",
]

# 先写到一个文件里
with open("D:/Python_study/output/invoices.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

# 再按行读出来，累计金额
total = 0
with open("D:/Python_study/output/invoices.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()          # 去掉换行符
        parts = line.split(",")      # 按逗号拆分
        amount = float(parts[1])     # 金额是第2列
        total += amount

print(f"发票总金额: {total} USD")

# ==================== 4. 读写 CSV 文件 ====================
# 场景：把发票明细写成表格，方便 Excel 打开
invoices = [
    ["客户", "报关单号", "金额(USD)", "币种"],
    ["A公司", "001", 1200, "USD"],
    ["B公司", "002", 3500, "USD"],
    ["C公司", "003", 900, "USD"],
]

with open("D:/Python_study/output/invoices.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(invoices)

print("CSV 已写入")

# 读 CSV
with open("D:/Python_study/output/invoices.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)

# ==================== 5. 小挑战 ====================
# 读取刚写的 CSV，只打印金额 >= 1000 的记录
print("--- 大额发票记录 ---")
with open("D:/Python_study/output/invoices.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    header = next(reader)  # 跳过表头
    for row in reader:
        if float(row[2]) >= 1000:
            print(row)
