"""为月度报表生成器造演示数据：6 个月的 Excel"""
from pathlib import Path
from openpyxl import Workbook

folder = Path("monthly_sales")
folder.mkdir(exist_ok=True)

# 数据：月份 → [(销售员, 销售额), ...]
months = {
    "2026-01": [("张三", 12000), ("李四", 8500), ("王五", 15300), ("赵六", 4200)],
    "2026-02": [("张三", 13500), ("李四", 9000), ("王五", 9800),  ("钱七", 7600)],
    "2026-03": [("张三", 11800), ("李四", 11200),("王五", 14200), ("赵六", 5800)],
    "2026-04": [("张三", 15600), ("李四", 9500), ("王五", 16500), ("钱七", 8800)],
    "2026-05": [("张三", 14200), ("李四", 10500),("王五", 13800), ("赵六", 6500), ("钱七", 7200)],
    "2026-06": [("张三", 16800), ("李四", 11000),("王五", 17500), ("赵六", 7100), ("钱七", 9300)],
}

for month, sales in months.items():
    wb = Workbook()
    ws = wb.active
    ws.append(("月份", "销售员", "销售额"))
    for person, amount in sales:
        ws.append((month, person, amount))
    out = folder / f"sales_{month}.xlsx"
    wb.save(out)

print(f"已造 {len(months)} 个月的销售数据到 {folder}/")