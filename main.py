# main.py —— 主程序
from mytools import calculate_bmi, celsius_to_fahrenheit, shout

print("=== 我的工具箱 ===")
print(f"BMI：{calculate_bmi(70, 1.75):.2f}")
print(f"36°C = {celsius_to_fahrenheit(36):.1f}°F")
print(shout("Python 好玩"))
