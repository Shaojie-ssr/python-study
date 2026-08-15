# lesson2.py - lambda 匿名函数练习
# 目标：学会 lambda 配合 sorted/map/filter 使用

# ==================== 1. 基础 lambda ====================
add = lambda x, y: x + y
print("10 + 20 =", add(10, 20))

square = lambda x: x ** 2
print("5 的平方 =", square(5))

# ==================== 2. 用 lambda 给发票金额排序 ====================
# 场景：有 5 张发票的美元金额，想按"换算成人民币后"排序
invoices_usd = [1200, 850, 3000, 560, 2100]
rate = 7.2

# key= 后面放 lambda：告诉 sorted() 用"人民币金额"作为排序依据
sorted_by_cny = sorted(invoices_usd, key=lambda usd: usd * rate)
print("按人民币金额从小到大排序:", sorted_by_cny)

# ==================== 3. 用 lambda 筛选大额发票 ====================
# 场景：只保留金额 >= 1000 美元的发票
big_invoices = list(filter(lambda usd: usd >= 1000, invoices_usd))
print("大额发票（>=1000 USD）:", big_invoices)

# ==================== 4. 用 lambda 批量换算 ====================
# 场景：把所有 USD 金额换算成 CNY
cny_list = list(map(lambda usd: round(usd * rate, 2), invoices_usd))
print("人民币金额列表:", cny_list)

# ==================== 5. 小挑战 ====================
# 把发票金额按"从大到小"排，用 lambda 写
sorted_desc = sorted(invoices_usd, key=lambda usd: usd, reverse=True)
print("从大到小排序:", sorted_desc)
