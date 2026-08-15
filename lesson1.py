# lesson1.py —— 第1课练习：美元 → 人民币换算
# 知识点：函数返回多个值（return a, b → 外面 a, b = 函数()）

def usd_to_cny(usd, rate=7.2):
    """美元 → 人民币，返回两个值：（人民币金额, 整数部分）"""
    cny = usd * rate          # ① 计算人民币金额
    whole = int(cny)          # ② int() 取整数部分（直接砍掉小数）
    return cny, whole         # ③ 返回两个值，自动打包成元组

# ---------- 调用 ----------
cny, whole = usd_to_cny(100) # ④ 解包：左边两个变量接住两个返回值
print(f"100 美元 = {cny:.2f} 元，整数部分是 {whole} 元")

# 再试一个：默认汇率之外的场景
cny2, whole2 = usd_to_cny(250, rate=7.15)
print(f"250 美元 = {cny2:.2f} 元，整数部分是 {whole2} 元")
