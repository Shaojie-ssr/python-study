"""按扩展名自动整理文件夹"""
import os
from pathlib import Path
from shutil import move

folder = Path("messy_folder")

# 文件类型 → 目标文件夹 的映射
type_map = {
    "xlsx": "Excel",
    "csv":  "Excel",
    "jpg":  "图片",
    "png":  "图片",
    "mp3":  "音频",
    "mp4":  "视频",
    "pdf":  "文档",
    "txt":  "文档",
    "md":   "文档",
    "py":   "代码",
    "json": "代码",
}

# 统计：每个类型有多少个
stats = {}

for f in folder.iterdir():
    if f.is_file():
        ext = f.suffix.lstrip(".").lower()    # "JPG" → "jpg"
        target_dir_name = type_map.get(ext, "其他")
        target_dir = folder / target_dir_name
        target_dir.mkdir(exist_ok=True)
        move(str(f), str(target_dir / f.name))
        stats[target_dir_name] = stats.get(target_dir_name, 0) + 1

print("整理完成 ✅")
for name, count in stats.items():
    print(f"  {name}: {count} 个文件")
