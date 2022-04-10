# 用途-Features
使用Mennaruuk/twayback(https://github.com/Mennaruuk/twayback)下载的tweets只是html文件。
可以使用这个脚本自动解析tweets中的图片，多线程并行快速地批量将图片下载下来。

# 使用方法-Usage
1. 使用twayback下载html文件命令示例，更详细命令请查看Mennaruuk/twayback(https://github.com/Mennaruuk/twayback)
python3 twayback.py -u kobebryant -to 2022-04-09

2. 再执行本程序
   python3 t_wayback_download.py "/Users/belber/Downloads/twayback/kobebryant"

3. 执行后可在kobebryant下img目录中看到下载好的所有图片，summary.txt列出了所有下载成功和失败的图片地址。
   