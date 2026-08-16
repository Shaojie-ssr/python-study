"""
小工具4：发票版本差异对比器
用途：对比两个版本的发票 CSV，找出 新增/删除/变化 的记录
练习：集合运算 + 字典查找 + CSV 读写 + 异常处理 + 函数多返回值
"""
import csv


# ==================== 1. 数据加载 ====================
def load_invoices(path):
    """读 CSV -> 字典 {单号: (客户, 金额)}，坏数据跳过"""
    records = {}
    errors = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # 跳过头行
            print(f"  读取 {path}（表头：{header}）")
            for row_num, row in enumerate(reader, start=2):
                try:
                    if len(row) != 3:
                        raise ValueError(f"应该 3 列，实际 {len(row)} 列")
                    invoice_id, customer, amount = row
                    records[invoice_id] = (customer, float(amount))
                except (ValueError, IndexError) as e:
                    errors.append((row_num, row, str(e)))
    except FileNotFoundError:
        print(f"  ❌ 文件不存在：{path}")
    return records, errors


# ==================== 2. 对比逻辑 ====================
def diff_invoices(v1, v2):
    """对比两版发票，返回 (新增, 删除, 变化)"""
    keys_v1 = set(v1.keys())
    keys_v2 = set(v2.keys())

    added = keys_v2 - keys_v1           # 仅 v2 有 -> 新增
    removed = keys_v1 - keys_v2         # 仅 v1 有 -> 删除
    common = keys_v1 & keys_v2          # 都有

    changed = []
    for k in common:
        if v1[k] != v2[k]:
            changed.append((k, v1[k], v2[k]))

    return added, removed, changed


# ==================== 3. 输出报告 ====================
def print_report(v1_path, v2_path, added, removed, changed, v1, v2):
    print("\n" + "=" * 60)
    print(f"📊 发票差异对比报告")
    print(f"   v1: {v1_path}  ({len(v1)} 条)")
    print(f"   v2: {v2_path}  ({len(v2)} 条)")
    print("=" * 60)

    if added:
        print(f"\n🆕 新增 {len(added)} 条（v1 没有，v2 有）：")
        for k in sorted(added):
            customer, amount = v2[k]
            print(f"   + {k}  {customer:<10} {amount:>10.2f} USD")

    if removed:
        print(f"\n🗑️  删除 {len(removed)} 条（v1 有，v2 没有）：")
        for k in sorted(removed):
            customer, amount = v1[k]
            print(f"   - {k}  {customer:<10} {amount:>10.2f} USD")

    if changed:
        print(f"\n🔄 变化 {len(changed)} 条（同一单号内容不同）：")
        # 用 lambda 按「金额变化幅度」从大到小排序
        for k, old, new in sorted(changed, key=lambda x: abs(x[2][1] - x[1][1]), reverse=True):
            print(f"   ~ {k}  {old[0]}: {old[1]:>9.2f} -> {new[1]:>9.2f}  (差额 {new[1]-old[1]:+.2f})")

    if not (added or removed or changed):
        print("\n✅ 两版完全一致，无差异")

    print("=" * 60)


# ==================== 4. 主流程 ====================
def main():
    print("===== 发票差异对比器 =====\n")

    print("📂 加载两个版本...")
    v1, err1 = load_invoices("data/invoices_v1.csv")
    v2, err2 = load_invoices("data/invoices_v2.csv")

    if err1 or err2:
        print(f"\n⚠️ 数据问题：v1 有 {len(err1)} 条坏数据，v2 有 {len(err2)} 条坏数据")

    if not v1 or not v2:
        print("\n❌ 数据加载失败，程序退出")
        return

    print("\n🔍 对比中...")
    added, removed, changed = diff_invoices(v1, v2)

    print_report("data/invoices_v1.csv", "data/invoices_v2.csv",
                 added, removed, changed, v1, v2)

    # 顺手把变化明细存一份文件
    if changed:
        with open("data/changes.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["单号", "v1客户", "v1金额", "v2客户", "v2金额", "差额"])
            for k, old, new in sorted(changed, key=lambda x: abs(x[2][1] - x[1][1]), reverse=True):
                diff = new[1] - old[1]
                writer.writerow([k, old[0], old[1], new[0], new[1], f"{diff:+.2f}"])
        print(f"\n💾 变化明细已保存：data/changes.csv")


if __name__ == "__main__":
    main()
