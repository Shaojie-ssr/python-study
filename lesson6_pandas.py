"""
阶段2 第1课：pandas 基础
======================
pandas 是 Python 数据处理的核弹级武器。
阶段1你用 csv 库一行行读数据，现在用 pandas 一行搞定。

本课学什么：
  1. pandas vs csv 库的区别
  2. DataFrame 和 Series 是什么
  3. 读取 CSV
  4. 查看数据（head/info/describe）
  5. 选择列和行
  6. 筛选过滤（布尔索引）
  7. 排序
  8. 新增计算列
  9. 简单统计

运行方式：python lesson6_pandas.py
"""

import pandas as pd  # 约定俗成缩写为 pd

print("=" * 60)
print("阶段2 第1课：pandas 基础")
print("=" * 60)


# ──────────────────────────────────────────────
# 1. 读取 CSV —— 一行搞定
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("1. 读取 CSV：pd.read_csv()")
print("─" * 60)

# 阶段1你的写法：
#   import csv
#   with open('data.csv') as f:
#       reader = csv.DictReader(f)
#       rows = list(reader)
# 这要 4 行，而且 rows 是一堆字典，处理不方便。

# pandas 一行：
df = pd.read_csv("data/invoices_full.csv")

# df 就是一个 DataFrame，你可以理解为「一张 Excel 表」
print("读取成功！数据长这样：")
print(df)


# ──────────────────────────────────────────────
# 2. 查看数据 —— 先看再动手
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("2. 查看数据")
print("─" * 60)

# 2.1 看前 5 行（默认 5 行，可以传数字 head(3)）
print("\n【head() —— 看前 5 行】")
print(df.head())

# 2.2 看后 3 行
print("\n【tail(3) —— 看后 3 行】")
print(df.tail(3))

# 2.3 看形状（行数, 列数）
print(f"\n【shape —— 数据规模】")
print(f"行数 × 列数：{df.shape}")  # (20, 10)

# 2.4 看列名
print(f"\n【columns —— 所有列名】")
print(list(df.columns))

# 2.5 看每列的数据类型
print(f"\n【dtypes —— 每列数据类型】")
print(df.dtypes)
# object = 字符串，int64 = 整数，float64 = 小数

# 2.6 info() —— 一键看全貌（列名、类型、非空数量）
print(f"\n【info() —— 数据全貌】")
df.info()


# ──────────────────────────────────────────────
# 3. describe() —— 统计摘要
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("3. describe() —— 数值列的统计摘要")
print("─" * 60)

# 自动对数值列算：count/mean/std/min/25%/50%/75%/max
print(df.describe())

# 对文本列做统计（include='object'）
print("\n【文本列统计 include='object'】")
print(df.describe(include="object"))
# unique = 去重后有几个值，top = 出现最多的值，freq = 出现次数


# ──────────────────────────────────────────────
# 4. 选择数据 —— 列和行
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("4. 选择数据")
print("─" * 60)

# 4.1 选一列（返回 Series）
print("\n【选一列：df['客户']】")
print(df["客户"])  # 这叫 Series，一维数据

# 4.2 选多列（返回 DataFrame，用列表）
print("\n【选多列：df[['客户', '金额', '币种']]】")
print(df[["客户", "金额", "币种"]])

# 4.3 按位置选行：iloc（index location）
print("\n【iloc[0] —— 第 1 行】")
print(df.iloc[0])  # 第 1 行，返回 Series

# 4.4 iloc 切片：前 3 行
print("\n【iloc[0:3] —— 前 3 行】")
print(df.iloc[0:3])

# 4.5 loc 按标签选行列：前 3 行的 客户 + 金额
print("\n【loc：前3行，指定列】")
print(df.loc[0:2, ["客户", "金额"]])


# ──────────────────────────────────────────────
# 5. 筛选过滤 —— 布尔索引
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("5. 筛选过滤（布尔索引）")
print("─" * 60)

# 5.1 单条件：只看 USD 的发票
print("\n【只看 USD 发票】")
usd = df[df["币种"] == "USD"]
print(usd[["客户", "发票号", "金额"]])
print(f"USD 发票共 {len(usd)} 笔")

# 5.2 多条件：USD 且金额 > 20000
print("\n【USD 且金额 > 20000】")
big_usd = df[(df["币种"] == "USD") & (df["金额"] > 20000)]
print(big_usd[["客户", "发票号", "金额"]])

# 5.3 字符串包含：客户名包含"上海"
print('\n【客户名包含"上海"】')
shanghai = df[df["客户"].str.contains("上海")]
print(shanghai[["客户", "发票号", "金额"]])

# 5.4 isin：指定多个值
print("\n【币种是 USD 或 EUR】")
usd_eur = df[df["币种"].isin(["USD", "EUR"])]
print(usd_eur[["客户", "币种", "金额"]])


# ──────────────────────────────────────────────
# 6. 排序
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("6. 排序 sort_values()")
print("─" * 60)

# 6.1 按金额降序
print("\n【按金额降序（最大的在最上面）】")
print(df.sort_values("金额", ascending=False)[["客户", "发票号", "金额"]].head(5))

# 6.2 多列排序：先按币种升序，再按金额降序
print("\n【先按币种升序，再按金额降序】")
print(df.sort_values(["币种", "金额"], ascending=[True, False])[["客户", "币种", "金额"]])


# ──────────────────────────────────────────────
# 7. 新增计算列
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("7. 新增计算列")
print("─" * 60)

# 汇率字典（演示用，实际应从 API 获取）
rates = {"USD": 7.2, "EUR": 7.8, "JPY": 0.05}

# 新增一列：人民币金额 = 外币金额 × 汇率
df["人民币金额"] = df["金额"] * df["币种"].map(rates)

# 新增一列：总金额验算 = 数量 × 单价
df["验算金额"] = df["数量"] * df["单价"]

print(df[["客户", "币种", "金额", "人民币金额", "验算金额"]].head(8))


# ──────────────────────────────────────────────
# 8. 简单统计
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("8. 简单统计")
print("─" * 60)

# 8.1 汇总
print(f"\n总发票笔数：{len(df)}")
print(f"外币总金额：{df['金额'].sum():,.2f}")
print(f"人民币总金额：{df['人民币金额'].sum():,.2f}")
print(f"平均单笔金额：{df['金额'].mean():,.2f}")
print(f"最大单笔金额：{df['金额'].max():,.2f}")
print(f"最小单笔金额：{df['金额'].min():,.2f}")

# 8.2 按客户统计笔数
print("\n【按客户统计笔数 value_counts()】")
print(df["客户"].value_counts())

# 8.3 按币种统计总金额
print("\n【按币种统计总金额】")
print(df.groupby("币种")["金额"].sum())

# 8.4 按客户统计：笔数 + 总金额 + 平均金额
print("\n【按客户汇总：笔数/总金额/平均金额】")
summary = df.groupby("客户").agg(
    笔数=("发票号", "count"),
    总金额=("金额", "sum"),
    平均金额=("金额", "mean"),
)
print(summary)

# 8.5 按目的国统计
print("\n【按目的国统计笔数和总金额】")
country_summary = df.groupby("目的国").agg(
    笔数=("发票号", "count"),
    总金额=("金额", "sum"),
).sort_values("总金额", ascending=False)
print(country_summary)


# ──────────────────────────────────────────────
# 9. 保存结果到 CSV
# ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("9. 保存结果到 CSV")
print("─" * 60)

# 把客户汇总存成新文件
summary.to_csv("data/customer_summary_pandas.csv", encoding="utf-8-sig")
# utf-8-sig 带 BOM，Excel 打开不乱码
print("已保存：data/customer_summary_pandas.csv")


# ──────────────────────────────────────────────
# 总结
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("本课总结")
print("=" * 60)
print("""
pandas 核心操作速记表：
┌──────────────────┬──────────────────────────────────┐
│ 操作             │ 代码                              │
├──────────────────┼──────────────────────────────────┤
│ 读 CSV           │ df = pd.read_csv('文件.csv')      │
│ 看前 N 行        │ df.head(N)                        │
│ 看形状           │ df.shape                          │
│ 看类型           │ df.dtypes / df.info()             │
│ 统计摘要         │ df.describe()                     │
│ 选一列           │ df['列名']                        │
│ 选多列           │ df[['列1','列2']]                 │
│ 选行             │ df.iloc[0:3] / df.loc[0:2,'列名'] │
│ 筛选             │ df[df['列'] > 值]                 │
│ 多条件           │ df[(条件1) & (条件2)]             │
│ 包含文字         │ df[df['列'].str.contains('文字')] │
│ 排序             │ df.sort_values('列', ascending=F) │
│ 新增列           │ df['新列'] = 计算表达式            │
│ 分组统计         │ df.groupby('列').agg(...)          │
│ 去重计数         │ df['列'].value_counts()           │
│ 存 CSV           │ df.to_csv('文件.csv')             │
└──────────────────┴──────────────────────────────────┘

口诀：读进来 head 看一眼，describe 统计一遍，
      布尔索引来筛选，groupby 分组好统计。
""")

print("✅ 阶段2 第1课完成！运行成功后截图发我，进入第2课。")
