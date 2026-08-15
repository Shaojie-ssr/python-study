"""数据分析第 1 节：pandas 核心概念演示"""
import pandas as pd

print("=" * 50)
print("1. 手动创建 DataFrame（从字典）")
print("=" * 50)

data = {
    "月份":   ["2026-01", "2026-01", "2026-01", "2026-01"],
    "销售员": ["张三", "李四", "王五", "赵六"],
    "销售额": [12000, 8500, 15300, 4200],
}
df = pd.DataFrame(data)
print(df)
print("\n形状（行数, 列数）:", df.shape)

print("\n" + "=" * 50)
print("2. 一列 = Series（取出来单独看）")
print("=" * 50)
s = df["销售额"]
print(type(s))          # pandas.core.series.Series
print(s)
print("这一列的和:", s.sum())

print("\n" + "=" * 50)
print("3. 从 Excel 直接读（你之前学的 openpyxl 底层在干活）")
print("=" * 50)
xlsx = pd.read_excel("monthly_sales/sales_2026-01.xlsx")
print(xlsx)
print("\n前 2 行 head(2):")
print(xlsx.head(2))

print("\n" + "=" * 50)
print("4. 快速看数据（分析师每天第一件事）")
print("=" * 50)
print("\n-- info() 看结构 --")
print(xlsx.info())
print("\n-- describe() 看数值统计 --")
print(xlsx["销售额"].describe())
print("\n-- 销售额的总和 / 平均 --")
print(f"总和: {xlsx["销售额"].max()}")
print(f"平均: {xlsx['销售额'].mean():.1f}")

print("\n" + "=" * 50)
print("5. 筛选（比 Excel 筛选强大 100 倍）")
print("=" * 50)
big = xlsx[xlsx["销售额"] >= 8500]
print("销售额 >= 8500 的记录：")
print(big)

print("\n" + "=" * 50)
print("第 1 节结束 ✅")
print("=" * 50)