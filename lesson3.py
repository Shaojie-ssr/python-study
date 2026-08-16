# lesson3.py - 数据结构进阶
# 目标：掌握列表推导式、元组、集合、字典常用操作

# ==================== 1. 列表推导式 ====================
# 场景：把一组美元金额快速换算成人民币
usd_list = [100, 250, 500, 1000, 2000]
rate = 7.2

# 老写法
# cny_list = []
# for usd in usd_list:
#     cny_list.append(usd * rate)

# 列表推导式：一行搞定
cny_list = [usd * rate for usd in usd_list]
print("人民币金额列表:", cny_list)

# 带条件的列表推导式：只保留 >= 500 美元的发票
cny_big = [usd * rate for usd in usd_list if usd >= 500]
print("大金额发票的人民币金额:", cny_big)

# ==================== 2. 元组 tuple ====================
# 场景：发票金额和税额一起存，不允许被误改
invoice = (10000, 900)   # （金额，税额）
print("元组发票:", invoice)
print("金额:", invoice[0], "税额:", invoice[1])

# invoice[0] = 20000  # 会报错，因为元组不可修改

# ==================== 3. 集合 set ====================
# 场景：统计合作过的客户名称，自动去重
raw_customers = ["A公司", "B公司", "A公司", "C公司", "B公司"]
unique_customers = set(raw_customers)
print("去重后的客户:", unique_customers)
print("客户数量:", len(unique_customers))

# 集合运算：本月 vs 上月客户
last_month = {"A公司", "B公司"}
this_month = {"B公司", "C公司"}
print("新客户:", this_month - last_month)       # 差集
print("共同客户:", this_month & last_month)     # 交集

# ==================== 4. 字典 dict 进阶 ====================
# 场景：记录客户对应的发票总额
invoice_map = {
    "A公司": 15000,
    "B公司": 28000,
    "C公司": 9000
}

# 遍历字典
for name, amount in invoice_map.items():
    print(f"{name}: {amount} 元")

# 安全取值（不会报错）
d_amount = invoice_map.get("D公司", 0)
print("D公司金额（默认值）:", d_amount)

# 字典推导式：所有金额打 95 折
discounted = {name: amount * 0.95 for name, amount in invoice_map.items()}
print("打折后:", discounted)

# ==================== 5. 小挑战 ====================
# 用字典推导式，只给金额 >= 10000 的客户打 9 折
vip_discount = {name: amount * 0.9 for name, amount in invoice_map.items() if amount >= 10000}
print("VIP 客户打折后:", vip_discount)
