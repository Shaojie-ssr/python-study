"""
阶段2 第3课：SQLite 数据库基础
==============================
SQLite 是一个「文件型数据库」，整个数据库就是一个 .db 文件。
不需要安装服务器，Python 自带 sqlite3 模块，开箱即用。

本课学什么：
  1. SQLite 是什么，跟 Excel/CSV 有什么区别
  2. 建表 CREATE TABLE
  3. 插入数据 INSERT
  4. 查询 SELECT / WHERE / ORDER BY / LIMIT
  5. 更新 UPDATE / 删除 DELETE
  6. Python 操作 sqlite3
  7. 参数化查询（防 SQL 注入）
  8. pandas 和 SQLite 互转

运行方式：python lesson8_sqlite.py
"""

import sqlite3
import pandas as pd
from datetime import date

print("=" * 70)
print("阶段2 第3课：SQLite 数据库基础")
print("=" * 70)


# ──────────────────────────────────────────────
# 0. 连接数据库（如果不存在就自动创建）
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("0. 连接数据库")
print("─" * 70)

DB_PATH = "data/export_business.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print(f"已连接数据库：{DB_PATH}")
print("SQLite 数据库就是一个普通文件，可以用资源管理器看到它。")


# ──────────────────────────────────────────────
# 1. 建表 CREATE TABLE
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("1. 建表 CREATE TABLE")
print("─" * 70)

# 先删除旧表（保证每次运行都是干净的）
cursor.execute("DROP TABLE IF EXISTS invoices;")
cursor.execute("DROP TABLE IF EXISTS customers;")

# 创建客户表
cursor.execute("""
CREATE TABLE customers (
    customer_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT,
    credit_level TEXT,
    cooperation_years INTEGER
);
""")
print("✅ 创建 customers 表")

# 创建发票表
cursor.execute("""
CREATE TABLE invoices (
    invoice_no TEXT PRIMARY KEY,
    invoice_date TEXT,
    customer_code TEXT,
    currency TEXT,
    amount REAL,
    declaration_no TEXT,
    product_name TEXT,
    destination TEXT,
    FOREIGN KEY (customer_code) REFERENCES customers(customer_code)
);
""")
print("✅ 创建 invoices 表")

# 常用数据类型：
# INTEGER  整数
# REAL     小数
# TEXT     文本
# DATE/TEXT 日期（SQLite 没有专门的日期类型，通常存 TEXT）
# PRIMARY KEY 主键，唯一标识一条记录
# FOREIGN KEY 外键，关联另一张表


# ──────────────────────────────────────────────
# 2. 插入数据 INSERT
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("2. 插入数据 INSERT")
print("─" * 70)

# 2.1 单条插入
cursor.execute("""
INSERT INTO customers (customer_code, name, country, credit_level, cooperation_years)
VALUES ('KH001', '上海海味鲜', '中国', 'A', 5);
""")

# 2.2 多条插入（用 executemany，效率更高）
customers_data = [
    ('KH002', '青岛海产达', '中国', 'B', 3),
    ('KH003', '大连渔港公司', '中国', 'A', 4),
    ('KH004', '烟台水产商行', '中国', 'B', 2),
    ('KH005', '宁波远洋渔业', '中国', 'C', 1),
]
cursor.executemany("""
INSERT INTO customers (customer_code, name, country, credit_level, cooperation_years)
VALUES (?, ?, ?, ?, ?);
""", customers_data)
print(f"✅ 插入 {len(customers_data) + 1} 个客户")

# 2.3 插入发票数据
invoices_data = [
    ('INV-2026-001', '2026-01-15', 'KH001', 'USD', 15800.00, '012345678901234567', '冷冻南美虾', '美国'),
    ('INV-2026-002', '2026-01-20', 'KH002', 'USD', 22500.00, '023456789012345678', '冷冻鳕鱼片', '日本'),
    ('INV-2026-003', '2026-02-03', 'KH001', 'USD', 31200.00, '034567890123456789', '冷冻南美虾', '美国'),
    ('INV-2026-004', '2026-02-10', 'KH003', 'EUR', 18900.00, '045678901234567890', '冷冻三文鱼', '德国'),
    ('INV-2026-005', '2026-02-18', 'KH002', 'USD', 9800.00, '056789012345678901', '冷冻鳕鱼片', '韩国'),
    ('INV-2026-006', '2026-03-01', 'KH004', 'JPY', 2100000.00, '067890123456789012', '冷冻章鱼', '日本'),
    ('INV-2026-007', '2026-03-12', 'KH001', 'USD', 27450.00, '078901234567890123', '冷冻南美虾', '美国'),
    ('INV-2026-008', '2026-03-20', 'KH003', 'EUR', 25200.00, '089012345678901234', '冷冻三文鱼', '法国'),
    ('INV-2026-009', '2026-04-05', 'KH002', 'USD', 16800.00, '090123456789012345', '冷冻鳕鱼片', '日本'),
    ('INV-2026-010', '2026-04-15', 'KH004', 'JPY', 1850000.00, '101234567890123456', '冷冻章鱼', '日本'),
]
cursor.executemany("""
INSERT INTO invoices (invoice_no, invoice_date, customer_code, currency, amount, declaration_no, product_name, destination)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
""", invoices_data)
print(f"✅ 插入 {len(invoices_data)} 张发票")

# 提交事务
conn.commit()
print("✅ 数据已提交到数据库")


# ──────────────────────────────────────────────
# 3. 查询数据 SELECT
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("3. 查询数据 SELECT")
print("─" * 70)

# 3.1 查询所有发票
cursor.execute("SELECT * FROM invoices;")
rows = cursor.fetchall()
print(f"\n【所有发票，共 {len(rows)} 条】")
for row in rows[:3]:
    print(row)

# 3.2 查询指定列
cursor.execute("SELECT invoice_no, customer_code, amount FROM invoices;")
print("\n【只查指定列】")
for row in cursor.fetchall()[:3]:
    print(row)

# 3.3 条件查询 WHERE
cursor.execute("SELECT * FROM invoices WHERE currency = 'USD';")
usd_rows = cursor.fetchall()
print(f"\n【USD 发票共 {len(usd_rows)} 条】")
for row in usd_rows:
    print(row)

# 3.4 多条件查询
cursor.execute("""
SELECT * FROM invoices
WHERE currency = 'USD' AND amount > 20000;
""")
print("\n【USD 且金额 > 20000】")
for row in cursor.fetchall():
    print(row)

# 3.5 排序 ORDER BY
cursor.execute("SELECT * FROM invoices ORDER BY amount DESC LIMIT 5;")
print("\n【金额 Top 5】")
for row in cursor.fetchall():
    print(row)

# 3.6 聚合查询 COUNT / SUM / AVG
cursor.execute("SELECT COUNT(*) FROM invoices;")
count = cursor.fetchone()[0]
print(f"\n发票总数：{count}")

cursor.execute("SELECT SUM(amount) FROM invoices WHERE currency = 'USD';")
usd_sum = cursor.fetchone()[0]
print(f"USD 总金额：{usd_sum:,.2f}")

cursor.execute("SELECT AVG(amount) FROM invoices;")
avg = cursor.fetchone()[0]
print(f"平均金额：{avg:,.2f}")


# ──────────────────────────────────────────────
# 4. JOIN 联表查询
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("4. JOIN 联表查询")
print("─" * 70)

cursor.execute("""
SELECT i.invoice_no, c.name, i.currency, i.amount, i.destination
FROM invoices i
JOIN customers c ON i.customer_code = c.customer_code
WHERE i.currency = 'USD'
ORDER BY i.amount DESC;
""")
print("\n【发票 + 客户名称（USD 降序）】")
for row in cursor.fetchall():
    print(row)

# JOIN 类型：
# INNER JOIN / JOIN     只返回两表匹配的行
# LEFT JOIN             返回左表所有行，右表没匹配填 NULL
# RIGHT JOIN            SQLite 不支持（但 MySQL/PostgreSQL 支持）


# ──────────────────────────────────────────────
# 5. GROUP BY 分组统计
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("5. GROUP BY 分组统计")
print("─" * 70)

cursor.execute("""
SELECT customer_code, COUNT(*) AS invoice_count, SUM(amount) AS total_amount
FROM invoices
GROUP BY customer_code
ORDER BY total_amount DESC;
""")
print("\n【按客户分组：笔数、总金额】")
for row in cursor.fetchall():
    print(row)

cursor.execute("""
SELECT destination, COUNT(*) AS cnt, SUM(amount) AS total
FROM invoices
GROUP BY destination
ORDER BY total DESC;
""")
print("\n【按目的国分组：笔数、总金额】")
for row in cursor.fetchall():
    print(row)


# ──────────────────────────────────────────────
# 6. 更新 UPDATE / 删除 DELETE
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("6. 更新 UPDATE / 删除 DELETE")
print("─" * 70)

# 6.1 更新：把 KH005 的合作年限改成 2 年
cursor.execute("""
UPDATE customers SET cooperation_years = 2 WHERE customer_code = 'KH005';
""")
conn.commit()
print("✅ 更新 KH005 合作年限为 2 年")

# 验证
cursor.execute("SELECT * FROM customers WHERE customer_code = 'KH005';")
print(cursor.fetchone())

# 6.2 删除：删除 KH005（先删关联发票，避免外键约束报错）
cursor.execute("DELETE FROM invoices WHERE customer_code = 'KH005';")
cursor.execute("DELETE FROM customers WHERE customer_code = 'KH005';")
conn.commit()
print("✅ 删除 KH005 客户及其关联发票")


# ──────────────────────────────────────────────
# 7. 参数化查询（防 SQL 注入）
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("7. 参数化查询（重要！防 SQL 注入）")
print("─" * 70)

# ❌ 错误写法：直接拼接字符串，有 SQL 注入风险
# code = "KH001' OR '1'='1"
# cursor.execute(f"SELECT * FROM customers WHERE customer_code = '{code}';")

# ✅ 正确写法：用 ? 占位符，sqlite3 自动转义
code = "KH001"
cursor.execute("SELECT * FROM customers WHERE customer_code = ?;", (code,))
print(f"\n【参数化查询结果：{code}】")
print(cursor.fetchone())

# 多个参数
cursor.execute("""
SELECT * FROM invoices
WHERE currency = ? AND amount > ?;
""", ("USD", 20000))
print("\n【参数化多条件查询：currency=USD, amount>20000】")
for row in cursor.fetchall():
    print(row)


# ──────────────────────────────────────────────
# 8. pandas 和 SQLite 互转
# ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("8. pandas 和 SQLite 互转")
print("─" * 70)

# 8.1 pandas 读 SQLite（直接写 SQL）
df_from_sql = pd.read_sql_query("SELECT * FROM invoices;", conn)
print(f"\n【从 SQLite 读到 pandas：{len(df_from_sql)} 行】")
print(df_from_sql.head())

# 8.2 pandas 读 SQLite（复杂 SQL）
df_join = pd.read_sql_query("""
SELECT i.invoice_no, c.name AS customer_name, i.currency, i.amount
FROM invoices i
JOIN customers c ON i.customer_code = c.customer_code;
""", conn)
print("\n【JOIN 查询读到 pandas】")
print(df_join)

# 8.3 pandas DataFrame 写入 SQLite
df_new = pd.DataFrame({
    "invoice_no": ["INV-2026-011", "INV-2026-012"],
    "invoice_date": ["2026-05-01", "2026-05-02"],
    "customer_code": ["KH001", "KH002"],
    "currency": ["USD", "USD"],
    "amount": [30000.00, 25000.00],
    "declaration_no": ["212345678901234567", "223456789012345678"],
    "product_name": ["冷冻南美虾", "冷冻鳕鱼片"],
    "destination": ["美国", "日本"],
})

# if_exists='append' 追加到现有表
# index=False 不把 DataFrame 索引写进去
df_new.to_sql("invoices", conn, if_exists="append", index=False)
print("\n✅ 用 pandas 把 2 条新发票追加到 SQLite")

# 验证
cursor.execute("SELECT COUNT(*) FROM invoices;")
print(f"发票总数现在为：{cursor.fetchone()[0]}")


# ──────────────────────────────────────────────
# 9. 关闭连接
# ──────────────────────────────────────────────
conn.close()
print("\n✅ 数据库连接已关闭")


# ──────────────────────────────────────────────
# 总结
# ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("本课总结")
print("=" * 70)
print("""
SQLite 核心操作速记表：
┌──────────────────┬─────────────────────────────────────────────┐
│ 操作             │ SQL / Python 代码                            │
├──────────────────┼─────────────────────────────────────────────┤
│ 连接数据库       │ sqlite3.connect('文件.db')                   │
│ 获取游标         │ conn.cursor()                                │
│ 建表             │ CREATE TABLE 表名 (...)                      │
│ 插入单条         │ INSERT INTO 表名 VALUES (...)                │
│ 插入多条         │ cursor.executemany(sql, 列表)                 │
│ 查询             │ SELECT * FROM 表名 WHERE 条件                │
│ 排序             │ ORDER BY 列 DESC/ASC                         │
│ 限制条数         │ LIMIT N                                      │
│ 聚合             │ COUNT/SUM/AVG/MAX/MIN                        │
│ 分组             │ GROUP BY 列                                  │
│ 联表             │ SELECT ... FROM A JOIN B ON A.x = B.x        │
│ 更新             │ UPDATE 表名 SET 列=值 WHERE 条件             │
│ 删除             │ DELETE FROM 表名 WHERE 条件                  │
│ 提交事务         │ conn.commit()                                │
│ 参数化查询       │ cursor.execute(sql, (值1, 值2))               │
│ pandas 读 SQL    │ pd.read_sql_query(sql, conn)                 │
│ pandas 写 SQL    │ df.to_sql('表名', conn, if_exists='append')  │
│ 关闭连接         │ conn.close()                                 │
└──────────────────┴─────────────────────────────────────────────┘

口诀：
  连接库、拿游标、建表插入要 commit；
  SELECT WHERE ORDER BY，JOIN GROUP BY 做统计；
  参数化防注入，pandas 读写更方便。
""")

print("✅ 阶段2 第3课完成！运行成功后截图发我，进入第4课（requests 调用 API）。")
