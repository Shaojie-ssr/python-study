"""pandas 第 3 节：matplotlib 数据可视化"""
import matplotlib
matplotlib.use("Agg")                                              # 无 GUI 也能保存
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False                  # 负号正常显示

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# --- 1. 读全部 6 个月的明细 ---
files = sorted(Path("monthly_sales").glob("sales_*.xlsx"))
df = pd.concat([pd.read_excel(f) for f in files], ignore_index=True)
print(f"载入 {len(df)} 条记录")
print()

# --- 2. 折线图：每月总销售额趋势 ---
monthly = df.groupby("月份")["销售额"].sum()
plt.figure(figsize=(10, 5))
plt.plot(monthly.index, monthly.values, marker="o", linewidth=2.5, color="#378ADD", markersize=8)
plt.title("月度销售趋势", fontsize=15)
plt.xlabel("月份")
plt.ylabel("销售额（元）")
plt.grid(True, alpha=0.3)
plt.xticks(rotation=30)
for x, y in zip(monthly.index, monthly.values):
    plt.annotate(f"{y:,}", (x, y), textcoords="offset points", xytext=(0, 10),
                 ha="center", fontsize=10, color="#333333")
plt.tight_layout()
plt.savefig("chart_line.png", dpi=120, bbox_inches="tight")
plt.close()
print("chart_line.png 已生成")

# --- 3. 柱状图：销售员总业绩 ---
by_person = df.groupby("销售员")["销售额"].sum().sort_values(ascending=False)
colors = ["#D85A30", "#EF9F27", "#378ADD", "#1D9E75", "#888780"]
plt.figure(figsize=(8, 5))
bars = plt.bar(by_person.index, by_person.values.max()), color=colors)
plt.title("销售员总业绩排名", fontsize=15)
plt.xlabel("销售员")
plt.ylabel("总销售额（元）")
for bar, v in zip(bars, by_person.values):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1000,
             f"{v:,}", ha="center", fontsize=10)
plt.tight_layout()
plt.savefig("chart_bar.png", dpi=120, bbox_inches="tight")
plt.close()
print("chart_bar.png 已生成")

# --- 4. 饼图：销售员业绩贡献占比 ---
plt.figure(figsize=(8, 6))
plt.pie(by_person.values, labels=by_person.index, autopct="%1.1f%%",
        colors=colors, startangle=90, textprops={"fontsize": 11})
plt.title("销售员业绩贡献占比", fontsize=15)
plt.axis("equal")
plt.tight_layout()
plt.savefig("chart_pie.png", dpi=120, bbox_inches="tight")
plt.close()
print("chart_pie.png 已生成")

print("\n三张图都已保存到 D:\\Python_study\\")
# --- 5. 进阶：双柱图（每人 + 每月，颜色分组）---
plt.figure(figsize=(10, 5))
for person, color in zip(by_person.index, colors):
    s = df[df["销售员"] == person].groupby("月份")["销售额"].sum()
    plt.plot(s.index, s.values, marker="o", label=person, linewidth=2, color=color)

plt.title("每人月度销售趋势对比", fontsize=15)
plt.xlabel("月份")
plt.ylabel("销售额（元）")
plt.legend(title="销售员")
plt.grid(True, alpha=0.3)
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("chart_trend_compare.png", dpi=120, bbox_inches="tight")
plt.close()
print("chart_trend_compare.png 已生成")
