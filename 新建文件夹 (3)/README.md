# 手写体图片生成器

把文字粘贴进来，一键生成逼真的手写作业图片。

## 效果

- 8 种真实手写字体随机混合，每个字独立选字体
- 红色横线作业本背景（A4 比例）
- 每行填满页面宽度，段落首行自动缩进
- 可选 1~20 页，自适应字号把内容塞进指定页数

## 用法

### 图形界面（推荐）

```bash
python handwriting.py
```

弹窗 → 粘贴文字 → 点按钮 → 图片生成到桌面 `手写作业` 文件夹。

**快捷键：** `Ctrl+Enter` 快速生成。

### 命令行

```bash
# 从 txt 文件生成（自动分页）
python handwriting.py input.txt

# 指定 3 页，自适应字号
python handwriting.py input.txt --pages 3

# 直接输入文字
python handwriting.py --text "你的文字内容"
```

### 桌面快捷方式

把 `handwriting.py` 的快捷方式放到桌面，拖拽 `.txt` 文件上去直接生成。

## 安装

```bash
pip install pillow
git clone https://github.com/lizixuan/Handwrite.git
cd Handwrite
python handwriting.py
```

## 字体

`font/` 目录下有 8 种手写字体（.ttf），可自行替换或添加。

## 许可

MIT
