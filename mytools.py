# mytools.py —— 我自己的工具箱

def calculate_bmi(weight_kg, height_m):
    """计算 BMI 指数"""
    return weight_kg / (height_m ** 2)

def celsius_to_fahrenheit(c):
    """摄氏 → 华氏"""
    return c * 9 / 5 + 32

def shout(text, times=3):
    """重复喊话 N 次"""
    return (" " + text) * times
