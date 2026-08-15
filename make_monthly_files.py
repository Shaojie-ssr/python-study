# make_monthly_files.py —— 生成 3 个月的销售分表（模拟"实际工作中的多文件"）
from openpyxl import Workbook

months_data = [
    ("1月", [("张三", 1000), ("李四", 800)]),
    ("2月", [("张三", 1200), ("李四", 900), ("王五", 1500)]),
    ("3月", [("张三", 1100), ("王五", 1600)]),
]

for month, sales in months_data:
    wb = Workbook()
    ws = wb.active
    ws.title = month
    ws.append(["销售员", "销售额"])
    for name, amount in sales:
        ws.append([name, amount])
    wb.save(f"sales_{month}.xlsx")
    print(f"sales_{month}.xlsx 已生成")