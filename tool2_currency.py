# tool2_currency.py - 小工具2：多币种开票金额换算器
# 功能：输入币种 + 金额，自动换算成人民币；支持 USD/EUR/JPY
# 练习重点：字典查询、input交互、try/except、循环控制

RATES = {
    "USD": 7.2,   # 美元
    "EUR": 7.8,   # 欧元
    "JPY": 0.048, # 日元
    "KRW": 0.0052 # 韩元
}


def convert(currency, amount):
    """
    把外币金额换算成人民币
    返回 (cny金额, 错误信息)
    如果币种不支持，cny为None，err为错误说明
    """
    rate = RATES.get(currency.upper())
    if rate is None:
        return None, f"❌ 不支持的币种：{currency}"
    return amount * rate, None


def show_supported():
    """打印支持的币种列表"""
    print("支持的币种：", ", ".join([f"{k}(汇率{RATES[k]})" for k in RATES]))


def main():
    print("=" * 40)
    print("多币种开票金额换算器")
    print("输入币种 + 金额，自动换算成 CNY")
    print("输入 exit 退出")
    print("=" * 40)
    show_supported()
    print()

    while True:
        # ① 读币种
        raw = input("请输入币种（USD/EUR/JPY/KRW）：").strip()
        if raw.lower() == "exit":
            print("bye bye 👋")
            break

        currency = raw.upper()
        if currency not in RATES:
            print(f"❌ 不支持 {currency}，请重新输入\n")
            continue

        # ② 读金额（这里用 try/except 防止用户乱输）
        amount_str = input("请输入金额：").strip()
        try:
            amount = float(amount_str)
        except ValueError:
            print(f"❌ '{amount_str}' 不是有效数字，请重新输入\n")
            continue

        # ③ 换算
        cny, err = convert(currency, amount)
        if err:
            print(err + "\n")
        else:
            rate = RATES[currency]
            print(f"💱 {amount:,.2f} {currency} × {rate} = {cny:,.2f} CNY\n")


if __name__ == "__main__":
    main()
