"""pandas 第 2 节：groupby 分组聚合"""
import pandas as pd
from pathlib import Path

# --- 1. 读全部 6 个月的明细 ---
files = sorted(Path("monthly_sales").glob("sales_*.xlsx"))
print(f"找到 {len(files)} 个月度文件")
all_dfs = [pd.read_excel(f) for f in files]
df = pd.concat(all_dfs, ignore_index=True)
print(f"合并后总行数：{len(df)}")
print(f"总销售额：{df['销售额'].sum():,.0f}")
print()

# --- 2. 按销售员分组 ---
print("=" * 50)
print("按销售员分组（每个销售员的总销售额）")
print("=" * 50)
by_person = df.groupby("销售员")["销售额"].sum()
print(by_person.sort_values(ascending=False))
print()

# --- 3. 按月份分组 ---
print("=" * 50)
print("按月份分组（每月的总销售额）")
print("=" * 50)
by_month = df.groupby("月份")["销售额"].sum()
print(by_month.sort_index())
print()

# --- 4. 多维度分组（销售员 + 月份）---
print("=" * 50)
print("二维透视：销售员 × 月份")
print("=" * 50)
pivot = df.groupby(["销售员", "月份"])["销售额"].sum().unstack()
print(pivot)
print()

# --- 5. 多种聚合同时算（sum / mean / count）---
print("=" * 50)
print("每个销售员的 总销售额 / 平均单笔 / 成交笔数")
print("=" * 50)
agg = df.groupby("销售员")["销售额"].agg(["sum", "mean", "count"])
agg.columns = ["总销售额", "平均单笔", "成交笔数"]
print(agg.sort_values("总销售额", ascending=False))
print()

# --- 6. 销冠是哪个 ---
top = by_person.idxmax()
top_amount = by_person.max()
print(f"🏆 销冠：{top}，共 {top_amount:,.0f} 元")
# A. 找张三最猛的一单是哪月哪月
zhang = df[df["销售员"] == "张三"]
best = zhang.loc[zhang["销售额"].idxmax()]
print(f"张三最猛的一单：{best['月份']} 卖了 {best['销售额']} 元")

# B. 每月平均客单价（这月总销售 / 这月成交笔数）
monthly = df.groupby("月份")["销售额"].agg(["sum", "count"])
monthly["平均客单价"] = monthly["sum"] / monthly["count"]
print(monthly)
pivot = df.groupby(["销售员", "月份"])["销售额"].sum().unstack()
pivot.to_excel("透视表.xlsx")
print("透视表.xlsx 已生成 ✅")
