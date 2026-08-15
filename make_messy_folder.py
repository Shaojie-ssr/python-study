"""生成一个杂乱的文件夹（用于演示整理）"""
import shutil
from pathlib import Path

folder = Path("messy_folder")

# 一刀切：整个文件夹删掉再重建（不管里面是文件还是子目录）
if folder.exists():
    shutil.rmtree(folder)        # rmtree = 递归删除整个文件夹
folder.mkdir()

files = [
    "report.xlsx", "photo.jpg", "photo.png",
    "notes.txt", "memo.txt", "data.csv",
    "sales.xlsx", "image.jpg", "summary.pdf",
    "readme.md", "log.txt", "song.mp3",
    "video.mp4", "code.py", "config.json",
]
for name in files:
    (folder / name).write_text("test", encoding="utf-8")

print(f"已造 {len(files)} 个文件到 messy_folder/")
