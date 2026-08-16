# tool5_validate.py - 报关单字段校验器
# 综合练习：文件读写 / 函数多返回值 / 异常处理 / 集合 / 字典 / lambda 排序
import csv
import re
from datetime import datetime

# ==================== 1. 单条记录的校验规则 ====================

# 合法客户名单（实际工作中可换成字典查表或数据库查）
KNOWN_CUSTOMERS = {"A公司", "B公司", "C公司", "D公司", "E公司"}

# 报关单号：必须 18 位数字
DECLARATION_NO_PATTERN = re.compile(r"^\d{18}$")

# 日期格式：YYYY-MM-DD
DATE_FORMAT = "%Y-%m-%d"

# 金额范围：100 ~ 1,000,000 USD
MIN_AMOUNT = 100
MAX_AMOUNT = 1_000_000


def validate_record(row):
    """校验一条报关单记录，返回 (是否合格, 错误列表)。"""
    errors = []

    # ---- 1. 报关单号 ----
    no = (row.get("单号") or "").strip()
    if not no:
        errors.append("单号为空")
    elif not DECLARATION_NO_PATTERN.fullmatch(no):
        errors.append(f"单号格式错误（需18位数字，实际 {len(no)} 位）: '{no}'")

    # ---- 2. 日期 ----
    date = (row.get("日期") or "").strip()
    if not date:
        errors.append("日期为空")
    else:
        try:
            datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            errors.append(f"日期格式错误（需 YYYY-MM-DD）: '{date}'")

    # ---- 3. 金额 ----
    amount_str = (row.get("金额") or "").strip()
    if not amount_str:
        errors.append("金额为空")
    else:
        try:
            amount = float(amount_str)
            if amount < MIN_AMOUNT:
                errors.append(f"金额过小（< {MIN_AMOUNT}）: {amount}")
            elif amount > MAX_AMOUNT:
                errors.append(f"金额过大（> {MAX_AMOUNT}）: {amount}")
        except ValueError:
            errors.append(f"金额非数字: '{amount_str}'")

    # ---- 4. 客户 ----
    customer = (row.get("客户") or "").strip()
    if not customer:
        errors.append("客户为空")
    elif customer not in KNOWN_CUSTOMERS:
        errors.append(f"未知客户: '{customer}'")

    return (len(errors) == 0, errors)


# ==================== 2. 批量校验文件 ====================

def validate_file(path):
    """读 CSV 并逐行校验，返回 (合格列表, 不合格列表, 错误统计字典)。"""
    valid_records = []
    invalid_records = []
    error_stats = {}   # 错误类型 → 出现次数

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            ok, errors = validate_record(row)
            record = {
                "行号": idx,
                "单号": (row.get("单号") or "").strip(),
                "日期": (row.get("日期") or "").strip(),
                "客户": (row.get("客户") or "").strip(),
                "金额": (row.get("金额") or "").strip(),
            }
            if ok:
                valid_records.append(record)
            else:
                record["errors"] = errors
                invalid_records.append(record)
                # 错误类型统计：每条错误的前缀就是错误类型
                for err in errors:
                    # 提取错误类型（冒号前的部分）
                    err_type = err.split(":", 1)[0].split("（")[0].strip()
                    error_stats[err_type] = error_stats.get(err_type, 0) + 1

    return valid_records, invalid_records, error_stats


# ==================== 3. 报告打印 ====================

def print_report(file_path, valid, invalid, error_stats):
    total = len(valid) + len(invalid)
    print("=" * 60)
    print(f"📋 报关单字段校验报告")
    print(f"   文件: {file_path}")
    print(f"   总记录: {total} 条")
    print("=" * 60)
    print()

    # ---- 合格记录 ----
    print(f"✅ 合格 {len(valid)} 条:")
    if valid:
        print(f"   {'行号':<6}{'单号':<22}{'日期':<14}{'客户':<10}{'金额':>12}")
        print(f"   {'-'*60}")
        for r in valid:
            print(f"   {r['行号']:<6}{r['单号']:<22}{r['日期']:<14}{r['客户']:<10}{r['金额']:>12}")
    else:
        print("   (无)")
    print()

    # ---- 不合格记录 ----
    print(f"❌ 不合格 {len(invalid)} 条:")
    if invalid:
        for r in invalid:
            print(f"   第 {r['行号']} 行 [{r['单号'] or '(空单号)'} / {r['客户'] or '(空客户)'}]")
            for err in r["errors"]:
                print(f"     - {err}")
    else:
        print("   (无)")
    print()

    # ---- 错误类型统计 ----
    print("📊 错误类型统计（按出现次数从多到少）:")
    if error_stats:
        # 用 lambda 按次数排序
        sorted_errors = sorted(error_stats.items(), key=lambda x: x[1], reverse=True)
        for err_type, count in sorted_errors:
            bar = "█" * count
            print(f"   {err_type:<14} {count} 次 {bar}")
    else:
        print("   (无)")
    print()


# ==================== 4. 报告保存 ====================

def save_invalid_report(invalid, error_stats, output_path):
    """把不合格记录和错误统计写到一个 txt 文件里，方便发给客户/同事。"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("报关单校验不合格清单\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"不合格总数: {len(invalid)}\n")
        f.write("=" * 60 + "\n\n")

        for r in invalid:
            f.write(f"第 {r['行号']} 行: 单号={r['单号'] or '(空)'}, "
                    f"客户={r['客户'] or '(空)'}, 金额={r['金额'] or '(空)'}\n")
            for err in r["errors"]:
                f.write(f"  - {err}\n")
            f.write("\n")

        f.write("=" * 60 + "\n")
        f.write("错误类型统计:\n")
        for err_type, count in sorted(error_stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {err_type}: {count} 次\n")

    print(f"💾 不合格清单已保存：{output_path}")


# ==================== 5. 主流程 ====================

if __name__ == "__main__":
    INPUT_FILE = "data/declarations.csv"
    OUTPUT_FILE = "data/invalid_report.txt"

    print("📂 加载报关单数据...")
    valid, invalid, error_stats = validate_file(INPUT_FILE)
    print()

    print_report(INPUT_FILE, valid, invalid, error_stats)

    if invalid:
        save_invalid_report(invalid, error_stats, OUTPUT_FILE)
    else:
        print("🎉 全部记录合格，无需生成不合格清单")

    print("\n--- 校验结束 ---")