"""
阶段2 第2课：pandas 数据处理进阶
=================================
本课学什么：
  1. merge 合并（类似 SQL 的 JOIN）
  2. concat 拼接（上下/左右拼接表）
  3. 透视表 pivot_table
  4. 缺失值处理
  5. 重复值处理
  6. 数据类型转换
  7. 综合练习：清洗脏发票数据

运行方式：python lesson7_pandas_advanced.py
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("阶段2 第2课：pandas 数据处理进阶")
print("=" * 70)


# ──────────────────────────────────────────────
# 1. merge 合并 —— 把两个表按关键字段拼起来
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("1. merge 合并（相当于 SQL 的 JOIN）")
print("─" * 70)

# 发票主表（已有客户编码和客户名称）
inv = pd.read_csv("data/invoices_master.csv")
print("\n【发票主表前 3 行】")
print(inv.head(3))

# 客户信息表（客户编码、国家、信用等级、合作年限）
cust = pd.read_csv("data/customers.csv")
print("\n【客户信息表】")
print(cust)

# 用客户编码把两张表合并起来
merged = pd.merge(inv, cust, on="客户编码", how="left")
# on="客户编码"：按哪列拼
# how="left"：左连接，保留左边（发票表）所有行
print("\n【merge 后：发票 + 客户信息】")
print(merged[["发票号", "客户名称_x", "客户编码", "信用等级", "合作年限"]].head(8))

# 注意：客户名称在两张表都有，pandas 自动改名：客户名称_x（左表）、客户名称_y（右表）
# 可以在 merge 前把不要重复的列删掉

# 1.1 提前删除重复列，避免 _x/_y
inv2 = inv.drop(columns=["客户名称"])  # 发票表不要客户名称，从客户信息表取
merged2 = pd.merge(inv2, cust, on="客户编码", how="left")
print("\n【删除重复列后再 merge】")
print(merged2[["发票号", "客户编码", "客户名称", "信用等级", "合作年限"]].head(5))

# 1.2 按多个字段合并
# 比如一张表有 客户编码+日期，另一张表有 客户编码+日期+折扣率，可以 on=["客户编码", "日期"]


# ──────────────────────────────────────────────
# 2. concat 拼接 —— 上下堆叠或左右并排
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("2. concat 拼接")
print("─" * 70)

q2 = pd.read_csv("data/invoices_q2.csv")
q3 = pd.read_csv("data/invoices_q3.csv")

print(f"\nQ2 发票：{len(q2)} 行")
print(q2)
print(f"\nQ3 发票：{len(q3)} 行")
print(q3)

# 2.1 上下拼接（axis=0，默认）
all_quarters = pd.concat([q2, q3], axis=0, ignore_index=True)
print(f"\n【concat 上下拼接后：共 {len(all_quarters)} 行】")
print(all_quarters)
# ignore_index=True：重新生成 0,1,2...的索引

# 2.2 左右拼接（axis=1）—— 用的少，了解即可
# 把两张表的列并排拼起来
side_by_side = pd.concat([q2.reset_index(drop=True), q3.reset_index(drop=True)], axis=1)
print("\n【concat 左右拼接（axis=1）】")
print(side_by_side)


# ──────────────────────────────────────────────
# 3. 透视表 pivot_table
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("3. 透视表 pivot_table")
print("─" * 70)

# 透视表 = 按多个维度做交叉汇总
# 例：按 客户 × 目的国 统计金额总和
pivot = inv.pivot_table(
    values="金额",       # 要统计的值
    index="客户名称",    # 行方向
    columns="目的国",    # 列方向
    aggfunc="sum",       # 汇总方式
    fill_value=0,        # 空值填 0
)
print("\n【客户 × 目的国 金额透视表】")
print(pivot)

# 3.1 按 商品名称 × 币种 透视
pivot2 = inv.pivot_table(
    values="金额",
    index="商品名称",
    columns="币种",
    aggfunc="sum",
    fill_value=0,
)
print("\n【商品 × 币种 金额透视表】")
print(pivot2)

# 3.2 多个汇总方式
pivot3 = inv.pivot_table(
    values="金额",
    index="客户名称",
    aggfunc=["count", "sum", "mean"],
)
print("\n【每个客户：笔数、总金额、平均金额】")
print(pivot3)


# ──────────────────────────────────────────────
# 4. 缺失值处理
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("4. 缺失值处理")
print("─" * 70)

dirty = pd.read_csv("data/invoices_dirty.csv")
print("\n【脏数据原始表】")
print(dirty)

# 4.1 看每列有多少空值
print("\n【每列缺失值数量】")
print(dirty.isnull().sum())

# 4.2 删除空值行
dropped = dirty.dropna()
print("\n【dropna() 后：删除所有含空值的行】")
print(dropped)
print(f"剩余 {len(dropped)} 行（原 {len(dirty)} 行）")

# 4.3 删除指定列为空的行
dropped_amount = dirty.dropna(subset=["金额"])
print('\n【只删除"金额"为空的行】')
print(dropped_amount)

# 4.4 填充缺失值
filled = dirty.copy()
# 币种缺失的，填充为 "USD"（假设最常见）
filled["币种"] = filled["币种"].fillna("USD")
# 目的国缺失的，填充为 "未知"
filled["目的国"] = filled["目的国"].fillna("未知")
# 金额缺失的，填充为 0
filled["金额"] = filled["金额"].fillna(0)
print("\n【填充缺失值后】")
print(filled)


# ──────────────────────────────────────────────
# 5. 重复值处理
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("5. 重复值处理")
print("─" * 70)

# 5.1 看哪些行完全重复
print("\n【完全重复的行】")
print(dirty[dirty.duplicated(keep=False)])

# 5.2 删除完全重复的行
deduped = dirty.drop_duplicates()
print(f"\n【drop_duplicates() 后】原 {len(dirty)} 行 → {len(deduped)} 行")
print(deduped)

# 5.3 按指定列去重（比如同一发票号只保留一条）
# keep="first" 保留第一次出现的，keep="last" 保留最后一次
dedup_by_invoice = dirty.drop_duplicates(subset=["发票号"], keep="first")
print("\n【按发票号去重（保留第一条）】")
print(dedup_by_invoice)


# ──────────────────────────────────────────────
# 6. 数据类型转换
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("6. 数据类型转换")
print("─" * 70)

print("\n【脏数据原始 dtypes】")
print(dirty.dtypes)

# 金额列里混了 "invalid" 字符串，导致 pandas 把它读成 object（字符串）
# 需要转成数值，错误值变成 NaN
dirty["金额_清洗"] = pd.to_numeric(dirty["金额"], errors="coerce")
print("\n【pd.to_numeric(errors='coerce') 后】")
print(dirty[["发票号", "金额", "金额_清洗"]])
# errors="coerce"：转不了的变成 NaN（Not a Number）

# 日期列转 datetime
dirty["日期_清洗"] = pd.to_datetime(dirty["日期"], errors="coerce")
print("\n【日期列转 datetime 后】")
print(dirty[["发票号", "日期", "日期_清洗"]])


# ──────────────────────────────────────────────
# 7. 综合练习：清洗脏发票数据
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("7. 综合练习：清洗脏发票数据")
print("─" * 70)

# 清洗流水线：
# 1. 读数据
# 2. 删除完全重复行
# 3. 金额转数值，转不了的变 NaN
# 4. 删除金额为空或 <= 0 的行
# 5. 币种缺失的填 USD
# 6. 目的国缺失的填"未知"
# 7. 按发票号去重
# 8. 保存清洗后的文件

raw = pd.read_csv("data/invoices_dirty.csv")
print(f"原始数据：{len(raw)} 行")

clean = (
    raw
    .drop_duplicates()                              # 删除完全重复行
    .assign(金额=lambda x: pd.to_numeric(x["金额"], errors="coerce"))  # 金额转数值
    .dropna(subset=["金额"])                          # 删除金额为空
    .query("金额 > 0")                                # 金额必须 > 0
    .assign(币种=lambda x: x["币种"].fillna("USD"))   # 币种缺失填 USD
    .assign(目的国=lambda x: x["目的国"].fillna("未知"))  # 目的国缺失填 未知
    .drop_duplicates(subset=["发票号"], keep="first")  # 按发票号去重
)

print(f"\n清洗后：{len(clean)} 行")
print(clean)

# 保存
clean.to_csv("data/invoices_cleaned.csv", index=False, encoding="utf-8-sig")
print("\n已保存：data/invoices_cleaned.csv")


# ──────────────────────────────────────────────
# 总结
# ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("本课总结")
print("=" * 70)
print("""
pandas 进阶操作速记表：
┌──────────────────┬────────────────────────────────────────────┐
│ 操作             │ 代码                                        │
├──────────────────┼────────────────────────────────────────────┤
│ 合并表           │ pd.merge(left, right, on='键', how='left')  │
│ 上下拼接         │ pd.concat([df1, df2], axis=0)               │
│ 左右拼接         │ pd.concat([df1, df2], axis=1)               │
│ 透视表           │ df.pivot_table(values, index, columns, agg) │
│ 看缺失值         │ df.isnull().sum()                           │
│ 删除含空值行     │ df.dropna()                                 │
│ 删除指定列空值行 │ df.dropna(subset=['列'])                    │
│ 填充缺失值       │ df['列'].fillna(默认值)                      │
│ 看重复行         │ df.duplicated(keep=False)                   │
│ 删除重复行       │ df.drop_duplicates()                        │
│ 按列去重         │ df.drop_duplicates(subset=['列'])           │
│ 转数值           │ pd.to_numeric(df['列'], errors='coerce')    │
│ 转日期           │ pd.to_datetime(df['列'], errors='coerce')   │
│ 类型转换         │ df['列'].astype('类型')                      │
└──────────────────┴────────────────────────────────────────────┘

口诀：
  左右合并用 merge，上下堆叠 concat；
  交叉汇总 pivot_table，空值重复全 clean。
""")

print("✅ 阶段2 第2课完成！运行成功后截图发我，进入第3课（SQLite 数据库）。")
