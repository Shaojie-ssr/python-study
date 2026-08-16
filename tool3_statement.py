# tool3_statement.py - 小工具3：客户对账单生成器
# 功能：读取交易 CSV → 按客户分组 → 为每个客户生成一份对账单 txt 文件
# 练习重点：字典分组、批量写文件、字符串模板、目录创建

import csv
import os


def load_transactions(path):
    """读取交易记录，返回 [(客户, 日期, 报关单号, 金额), ...] 和错误列表"""
    records = []
    errors = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # 跳过表头
            for line_no, row in enumerate(reader, start=2):
                try:
                    customer = row[0].strip()
                    date = row[1].strip()
                    declaration = row[2].strip()
                    amount = float(row[3])
                    records.append((customer, date, declaration, amount))
                except (ValueError, IndexError):
                    errors.append(f"第 {line_no} 行数据异常：{row}")
    except FileNotFoundError:
        errors.append(f"文件不存在：{path}")
    return records, errors


def group_by_customer(records):
    """按客户分组，返回 {客户: [(日期, 报关单号, 金额), ...]}"""
    groups = {}
    for customer, date, declaration, amount in records:
        if customer not in groups:
            groups[customer] = []
        groups[customer].append((date, declaration, amount))
    return groups


def build_statement(customer, items):
    """根据客户交易列表，生成对账单文本"""
    lines = []
    lines.append("=" * 44)
    lines.append(f"          客户对账单")
    lines.append(f"客户名称：{customer}")
    lines.append("=" * 44)
    lines.append(f"{'日期':<12}{'报关单号':<16}{'金额(USD)':>12}")
    lines.append("-" * 44)

    total = 0
    for date, declaration, amount in items:
        lines.append(f"{date:<12}{declaration:<16}{amount:>12.2f}")
        total += amount

    lines.append("-" * 44)
    lines.append(f"{'合计':<28}{total:>12.2f}")
    lines.append("=" * 44)
    lines.append("本对账单仅供参考，如有疑问请联系财务部。")
    return "\n".join(lines), total


def generate_all_statements(groups, output_dir):
    """为每个客户生成独立的对账单文件"""
    os.makedirs(output_dir, exist_ok=True)
    grand_total = 0
    for customer, items in groups.items():
        text, total = build_statement(customer, items)
        grand_total += total
        # 文件名做简单处理：去掉特殊字符，避免创建文件失败
        safe_name = "".join(c for c in customer if c.isalnum() or c in ("_", "-"))
        file_path = os.path.join(output_dir, f"{safe_name}_statement.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ 已生成：{file_path}  金额合计：{total:.2f} USD")
    return grand_total


def main():
    os.makedirs("output", exist_ok=True)
    data_file = "output/transactions.csv"

    # 1. 如果没有示例数据，自动生成一份
    if not os.path.exists(data_file):
        sample = [
            ["客户", "日期", "报关单号", "金额(USD)"],
            ["A公司", "2026-08-01", "230120241201234567", "1200"],
            ["B公司", "2026-08-02", "230120241209876543", "3500"],
            ["A公司", "2026-08-05", "230120241205551111", "2800"],
            ["C公司", "2026-08-06", "230120241206662222", "900"],
            ["B公司", "2026-08-08", "230120241208773333", "1500"],
            ["A公司", "2026-08-10", "bad-data", "abc"],  # 坏数据
        ]
        with open(data_file, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(sample)

    # 2. 读取 + 分组 + 生成
    records, errors = load_transactions(data_file)
    print(f"成功读取 {len(records)} 条记录，{len(errors)} 条坏数据")
    for e in errors:
        print("⚠️", e)

    if records:
        groups = group_by_customer(records)
        print(f"\n共涉及 {len(groups)} 个客户，开始生成对账单...\n")
        grand_total = generate_all_statements(groups, "output/statements")
        print(f"\n💰 所有客户金额合计：{grand_total:.2f} USD")
    else:
        print("没有有效记录，未生成对账单。")


if __name__ == "__main__":
    main()
