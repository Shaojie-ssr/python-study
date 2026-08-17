# -*- coding: utf-8 -*-
"""
阶段2 第5课：ETL 数据管道综合项目（报关单 + 开票数据）

ETL = Extract(抽取) → Transform(转换) → Load(加载)

真实业务场景：
    报关行给你一份报关单 CSV，财务系统导出一份开票 CSV，
    你要把它们合并成一张「报关单-发票对照表」，入库保存，再生成 Excel 报表。

本课把阶段2学的 pandas + SQLite + openpyxl 全部串起来：
    Extract  : pandas 读取两份 CSV
    Transform: 去重 / 清洗金额 / 补缺失值 / 汇率换算 / 按报关单号关联
    Load     : 写入 SQLite 数据库（3 张表）
    Report   : 输出 Excel 汇总报表（4 个 sheet）
"""

import sqlite3
from pathlib import Path

import pandas as pd

# ============================================================
# 0. 准备工作：路径 + 汇率表
# ============================================================
BASE_DIR = Path(__file__).parent          # 脚本所在目录
DATA_DIR = BASE_DIR / "data"              # 数据目录
DB_PATH = DATA_DIR / "export_pipeline.db" # SQLite 数据库文件
XLSX_PATH = BASE_DIR / "export_summary.xlsx"  # Excel 报表

# 模拟汇率（真实场景可用第4课学的 requests 调 API 实时获取）
RATE = {"USD": 7.2, "JPY": 0.05, "CNY": 1.0}

print("=" * 60)
print("ETL 数据管道：报关单 × 开票 合并汇总")
print("=" * 60)


# ============================================================
# 1. Extract 抽取：读取两份 CSV
# ============================================================
def step1_extract():
    """从 CSV 读取报关单和开票数据"""
    decl = pd.read_csv(DATA_DIR / "declarations_export.csv")
    inv = pd.read_csv(DATA_DIR / "invoices_export.csv")

    print("\n【1. 抽取 Extract】")
    print(f"  报关单数据：{len(decl)} 行 × {decl.shape[1]} 列")
    print(f"  开票数据  ：{len(inv)} 行 × {inv.shape[1]} 列")
    print(f"  报关单列名：{list(decl.columns)}")
    print(f"  开票列名  ：{list(inv.columns)}")
    return decl, inv


# ============================================================
# 2. Transform 转换：清洗 + 关联
# ============================================================
def step2_transform(decl, inv):
    """清洗两份数据，按报关单号关联成一张总表"""
    print("\n【2. 转换 Transform】")

    # ---- 2.1 开票表去重（同一张发票被重复录入）----
    before = len(inv)
    inv = inv.drop_duplicates(subset=["发票号"], keep="first")
    print(f"  [去重] 开票表按发票号去重：{before} 行 → {len(inv)} 行")

    # ---- 2.2 金额清洗（可能有 "2,520" 带逗号 或 "abc" 乱数据）----
    for df in (decl, inv):
        col = "总价" if "总价" in df.columns else "金额"
        # 先去掉千位分隔符逗号，再强制转数字，转不了的变 NaN
        df[col] = df[col].astype(str).str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    bad_amount = inv["金额"].isna().sum() + decl["总价"].isna().sum()
    print(f"  [清洗] 金额转换：发现 {bad_amount} 条金额异常（已标为 NaN，稍后剔除）")

    # ---- 2.3 报关单目的国缺失值填充 ----
    missing_country = decl["目的国"].isna().sum()
    decl["目的国"] = decl["目的国"].fillna("未知")
    print(f"  [补缺] 目的国缺失 {missing_country} 条，已填充为「未知」")

    # ---- 2.4 剔除金额为 NaN 的坏数据 ----
    decl = decl.dropna(subset=["总价"])
    inv = inv.dropna(subset=["金额"])
    print(f"  [剔除] 坏数据清理后：报关单 {len(decl)} 行，开票 {len(inv)} 行")

    # ---- 2.5 汇率换算：给开票表加人民币金额列 ----
    inv["人民币金额"] = inv.apply(
        lambda r: round(r["金额"] * RATE.get(r["币种"], 1.0), 2), axis=1
    )
    print("  [换算] 已按汇率换算人民币金额（USD=7.2, JPY=0.05, CNY=1.0）")

    # ---- 2.6 按报关单号关联（merge = SQL 的 JOIN）----
    merged = pd.merge(inv, decl, on="报关单号", how="inner")
    orphan = inv[~inv["报关单号"].isin(decl["报关单号"])]
    print(f"  [关联] 成功关联 {len(merged)} 条；"
          f"有 {len(orphan)} 条开票找不到报关单（孤儿数据）")

    # ---- 2.7 补充：用单价×净重 校验报关总价是否一致 ----
    # 注意：单价是每公斤价格，所以用净重（KG）而不是件数！
    merged["计算总价"] = (merged["单价"] * merged["净重"]).round(2)
    mismatch = merged[abs(merged["计算总价"] - merged["总价"]) > 0.01]
    print(f"  [校验] 单价×净重 ≠ 总价 的有 {len(mismatch)} 条（可人工复核）")

    return decl, inv, merged


# ============================================================
# 3. Load 加载：写入 SQLite
# ============================================================
def step3_load(decl, inv, merged):
    """把清洗后的数据存入 SQLite 数据库（3 张表）"""
    print("\n【3. 加载 Load → SQLite】")

    # 数据库文件每次运行都重建，保证课程可重复运行
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)

    decl.to_sql("declarations", conn, index=False, if_exists="replace")
    inv.to_sql("invoices", conn, index=False, if_exists="replace")
    merged.to_sql("invoice_details", conn, index=False, if_exists="replace")

    print(f"  数据库：{DB_PATH.name}")
    print("  已建 3 张表：")
    print("    - declarations   (报关单, {0} 行)".format(len(decl)))
    print("    - invoices       (开票,   {0} 行)".format(len(inv)))
    print("    - invoice_details(关联总表, {0} 行)".format(len(merged)))

    # 演示用 SQL 查询验证入库结果
    cur = conn.execute("""
        SELECT 币制, COUNT(*) AS 张数, SUM(金额) AS 合计金额
        FROM invoice_details
        GROUP BY 币制
        ORDER BY 合计金额 DESC
    """)
    print("\n  [SQL 验证] 按币种统计：")
    for row in cur.fetchall():
        print(f"    {row[0]}：{row[1]} 张，合计 {row[2]}")

    conn.close()
    return DB_PATH


# ============================================================
# 4. Report 输出：Excel 汇总报表
# ============================================================
def step4_report(merged):
    """把关联后的数据导出为 Excel，含 4 个 sheet"""
    print("\n【4. 报表 Report → Excel】")

    # 选择要展示的列，避免太宽
    cols = ["发票号", "报关单号", "客户名称", "商品名称", "件数", "净重",
            "总价", "币制", "人民币金额", "目的国", "出口日期", "开票日期"]
    detail = merged[cols]

    # 按客户汇总
    by_customer = (
        merged.groupby("客户名称")
        .agg(报关单数=("报关单号", "count"),
             开票金额=("人民币金额", "sum"))
        .reset_index()
        .sort_values("开票金额", ascending=False)
    )

    # 按币种汇总
    by_currency = (
        merged.groupby("币制")
        .agg(发票数=("发票号", "count"), 原币合计=("金额", "sum"))
        .reset_index()
    )

    # 按目的国汇总
    by_country = (
        merged.groupby("目的国")
        .agg(报关单数=("报关单号", "count"),
             净重合计=("净重", "sum"))
        .reset_index()
        .sort_values("净重合计", ascending=False)
    )

    # 一个 Excel 文件 4 个 sheet
    with pd.ExcelWriter(XLSX_PATH, engine="openpyxl") as writer:
        detail.to_excel(writer, sheet_name="开票明细", index=False)
        by_customer.to_excel(writer, sheet_name="按客户汇总", index=False)
        by_currency.to_excel(writer, sheet_name="按币种汇总", index=False)
        by_country.to_excel(writer, sheet_name="按目的国汇总", index=False)

    print(f"  已生成报表：{XLSX_PATH.name}")
    print("  包含 4 个 sheet：开票明细 / 按客户汇总 / 按币种汇总 / 按目的国汇总")


# ============================================================
# 主流程
# ============================================================
def main():
    decl, inv = step1_extract()                    # 1. 抽取
    decl, inv, merged = step2_transform(decl, inv) # 2. 转换（返回清洗后的表）
    step3_load(decl, inv, merged)                  # 3. 加载
    step4_report(merged)                           # 4. 报表

    print("\n" + "=" * 60)
    print("==> 阶段2 第5课完成！一条数据管道跑通了。")
    print("=" * 60)
    print("""
本课口诀：
    抽取 CSV 两步走，转换清洗加关联；
    去重补缺转类型，汇率换算算钱款；
    入库 SQLite 三张表，Excel 四页看汇总；
    脏数据别怕慢慢清，管道跑通效率高。
""")


if __name__ == "__main__":
    main()
