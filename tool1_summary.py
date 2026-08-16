# tool1_summary.py - 小工具1：发票汇总器
# 功能：读取发票 CSV -> 按客户汇总金额 -> 换算人民币 -> 排序输出报表
# 综合运用：第1课多返回值 | 第2课lambda排序 | 第3课字典 | 第4课文件读写 | 第5课异常处理
import csv
import os

RATE = 7.0  # 美元汇率


def load_invoices(path):
    """读取发票CSV，返回 (有效记录, 错误信息) 两个值"""
    records = []   # 存有效数据：[(客户, 报关单号, 金额), ...]
    errors = []    # 存坏数据的提示
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # 跳过表头
            for line_no, row in enumerate(reader, start=2):  # start=2 因为第1行是表头
                try:
                    customer = row[0]
                    no = row[1]
                    amount = float(row[2])
                    records.append((customer, no, amount))
                except (ValueError, IndexError):
                    # 金额不是数字(ValueError) 或 列数不够(IndexError)
                    errors.append(f"第 {line_no} 行数据有问题：{row}，已跳过")
    except FileNotFoundError:
        errors.append(f"文件不存在：{path}")
    return records, errors   # <-- 第1课：一次返回两个值


def summarize(records):
    """按客户汇总金额，返回 {客户: 总金额USD}"""
    total = {}
    for customer, no, amount in records:   # <-- 解包元组
        total[customer] = total.get(customer, 0) + amount
    return total


def make_report(total):
    """按总金额从大到小排序，生成报表每一行"""
    ranked = sorted(total.items(), key=lambda x: x[1], )  # <-- 第2课：lambda
    lines = [f"{'客户':<8}{'总金额(USD)':>14}{'总金额(CNY)':>16}"]
    lines.append("-" * 40)
    for customer, amount in ranked:
        lines.append(f"{customer:<8}{amount:>14.2f}{amount * RATE:>16.2f}")
    lines.append("-" * 40)
    grand = sum(total.values())
    lines.append(f"{'合计':<8}{grand:>14.2f}{grand * RATE:>16.2f}")
    return lines


def main():
    os.makedirs("output", exist_ok=True)
    data_file = "output/invoices_raw.csv"

    # 1. 如果没有数据文件，先生成一份带"坏数据"的示例（模拟真实场景）
    if not os.path.exists(data_file):
        sample = [
            ["客户", "报关单号", "金额(USD)"],
            ["A公司", "001", "1200"],
            ["B公司", "002", "3500"],
            ["C公司", "003", "900"],
            ["A公司", "004", "abc"],    # 坏数据：金额不是数字
            ["B公司", "005", "800"],
            ["C公司", "006", "650"],
            ["坏行"],                    # 坏数据：缺列
        ]
        with open(data_file, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(sample)

    # 2. 读取数据（坏数据自动跳过并提示）
    records, errors = load_invoices(data_file)
    print(f"成功读取 {len(records)} 条记录，发现 {len(errors)} 条坏数据")
    for e in errors:
        print("⚠️", e)

    # 3. 汇总 + 生成报表
    total = summarize(records)
    lines = make_report(total)
    print()
    print("\n".join(lines))

    # 4. 报表保存成文件
    report_file = "output/report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n✅ 报表已保存：{report_file}")


if __name__ == "__main__":
    main()
