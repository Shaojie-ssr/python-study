# lesson5.py - 异常处理 try/except
# 目标：让程序遇到错误时不崩溃，给出友好提示

import os

# ==================== 1. 基本 try/except ====================
# 场景：用户输入金额，但可能输入了字母
def get_amount():
    user_input = input("请输入发票金额：")
    try:
        amount = float(user_input)
        return amount
    except ValueError:
        print(f"❌ 输入错误：'{user_input}' 不是有效数字，请重新输入")
        return None

amount = get_amount()
if amount is not None:
    print(f"金额为：{amount}")

# ==================== 2. 处理文件不存在 ====================
# 场景：读取一个可能不存在的文件
def read_log(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在：{path}")
        return ""

content = read_log("D:/Python_study/output/not_exist.txt")
print("读取结果：", content if content else "(空)")

# ==================== 3. 处理除零错误 ====================
# 场景：算税率，但分母可能为 0
def calc_tax_rate(tax, total):
    try:
        rate = tax / total
        return rate
    except ZeroDivisionError:
        print("❌ 总金额不能为 0")
        return 0

print(f"税率：{calc_tax_rate(900, 10000):.2%}")
print(f"税率：{calc_tax_rate(900, 0):.2%}")

# ==================== 4. 捕获多种异常 ====================
# 场景：读取 CSV 并转换金额，可能文件不存在、格式错误、金额非数字
def parse_invoice_line(line):
    try:
        name, amount_str = line.split(",")
        amount = float(amount_str)
        return name, amount
    except ValueError:
        print(f"❌ 格式或数字错误：{line}")
        return None, None
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        return None, None

print(parse_invoice_line("A公司,1200"))    # 正常
print(parse_invoice_line("B公司,abc"))     # 数字错误
print(parse_invoice_line("C公司"))         # 拆分错误

# ==================== 5. finally 和 else ====================
# finally：无论是否出错，都会执行（常用于收尾）
# else：只有没出错时才执行
def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("❌ 不能除以 0")
        return None
    else:
        print("✅ 计算成功")
        return result
    finally:
        print("--- 计算结束 ---")

print("结果：", safe_divide(10, 2))
print("结果：", safe_divide(10, 0))

# ==================== 6. 小挑战 ====================
# 写一个函数 safe_read_csv(path)，读取 CSV 文件
# - 文件不存在：返回空列表，并打印提示
# - 某行转换数字失败：跳过该行，打印提示
# - 成功：返回 [(客户, 金额), ...]
def safe_read_csv(path):
    result = []
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    name, amount_str = line.split(",")
                    amount = float(amount_str)
                    result.append((name, amount))
                except ValueError:
                    print(f"❌ 第 {i} 行格式或数字错误：{line}，已跳过")
    except FileNotFoundError:
        print(f"❌ 文件不存在：{path}")
    return result

# 先创建一个测试文件
os.makedirs("D:/Python_study/output", exist_ok=True)
with open("D:/Python_study/output/test_invoices.txt", "w", encoding="utf-8") as f:
    f.write("A公司,1000\n")
    f.write("B公司,2000\n")
    f.write("C公司,abc\n")   # 这行会出错
    f.write("D公司,3000\n")

print("\n--- 挑战结果 ---")
print(safe_read_csv("D:/Python_study/output/test_invoices.txt"))
print(safe_read_csv("D:/Python_study/output/no_file.txt"))
