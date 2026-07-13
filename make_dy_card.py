#!/usr/bin/env python3
"""
抖音跳转小卡片批量生成器
用法：python3 make_dy_card.py --title "标题" --desc "描述" --url "跳转地址" --filename "文件名"
生成后 git push 部署即可上线
"""
import argparse
import subprocess
import os

def generate_card(title, desc, url, filename):
    """生成一张抖音跳转卡片HTML"""
    
    # 预览图
    from PIL import Image, ImageDraw, ImageFont
    w, h = 400, 225
    img = Image.new('RGBA', (w, h), (0, 80, 212, 255))
    draw = ImageDraw.Draw(img)
    
    # 渐变背景
    for y in range(h):
        ratio = y / h
        r = int(26 + (0 - 26) * ratio)
        g = int(109 + (80 - 109) * ratio)
        b = int(255 + (212 - 255) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_desc = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_url = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_btn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        font_title = font_desc = font_url = font_btn = ImageFont.load_default()
    
    # 标题
    bbox1 = draw.textbbox((0,0), title, font=font_title)
    x1 = (w - (bbox1[2]-bbox1[0])) // 2
    draw.text((x1, 40), title, fill='white', font=font_title)
    
    # 描述
    bbox2 = draw.textbbox((0,0), desc, font=font_desc)
    x2 = (w - (bbox2[2]-bbox2[0])) // 2
    draw.text((x2, 95), desc, fill=(255,255,255,210), font=font_desc)
    
    # URL
    domain = url.replace('https://','').replace('http://','').rstrip('/')
    bbox3 = draw.textbbox((0,0), domain, font=font_url)
    x3 = (w - (bbox3[2]-bbox3[0])) // 2
    draw.text((x3, 130), domain, fill=(255,255,255,160), font=font_url)
    
    # 按钮
    btn_w, btn_h = 120, 32
    btn_x = (w - btn_w) // 2
    btn_y = 170
    draw.rounded_rectangle([btn_x, btn_y, btn_x+btn_w, btn_y+btn_h], radius=16, fill=(255,255,255,40), outline=(255,255,255,80))
    text4 = "立即领取"
    bbox4 = draw.textbbox((0,0), text4, font=font_btn)
    x4 = btn_x + (btn_w - (bbox4[2]-bbox4[0])) // 2
    y4 = btn_y + (btn_h - (bbox4[3]-bbox4[1])) // 2
    draw.text((x4, y4), text4, fill='white', font=font_btn)
    
    preview_file = filename.replace('.html', '-preview.png')
    img.save(preview_file, 'PNG')
    
    # HTML页面
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{title}</title>
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://guoguo99.xyz/{preview_file}">
<meta property="og:image:secure_url" content="https://guoguo99.xyz/{preview_file}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="400">
<meta property="og:image:height" content="225">
<meta property="og:type" content="website">
<meta property="og:url" content="https://guoguo99.xyz/{filename}">
<meta property="og:site_name" content="郭郭的实操资料">
<meta property="og:locale" content="zh_CN">
<meta name="description" content="{desc}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://guoguo99.xyz/{preview_file}">
<meta http-equiv="refresh" content="2;url={url}">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:100%;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;background:linear-gradient(135deg,#1a6dff 0%,#0050d4 100%);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;overflow:hidden;position:relative}}
body::before{{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 30% 30%,rgba(255,255,255,0.12) 0%,transparent 50%);pointer-events:none}}
.card{{width:280px;padding:30px 20px;background:rgba(255,255,255,0.12);border-radius:20px;backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.2);text-align:center;position:relative;z-index:1}}
.card h1{{font-size:24px;font-weight:700;margin-bottom:8px;letter-spacing:2px}}
.card p{{font-size:14px;opacity:0.8;margin-bottom:16px}}
.card .url{{font-size:12px;opacity:0.6;margin-bottom:20px}}
.btn{{display:inline-block;padding:10px 30px;background:#fff;color:#0050d4;border-radius:25px;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:1px}}
.hint{{margin-top:20px;font-size:11px;opacity:0.5;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:0.3}}50%{{opacity:0.7}}}}
</style>
</head>
<body>
<div class="card">
<h1>{title}</h1>
<p>{desc}</p>
<div class="url">{domain}</div>
<a href="{url}" class="btn">立即领取</a>
</div>
<div class="hint">2秒后自动跳转...</div>
<script>setTimeout(function(){{window.location.href='{url}'}},2000);</script>
</body>
</html>'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 卡片已生成: {filename} + {preview_file}")
    return filename, preview_file

def deploy(files):
    """git push 部署"""
    for f in files:
        subprocess.run(['git', 'add', f], check=True)
    subprocess.run(['git', 'commit', '-m', f'抖音卡片: {files[0]}'], check=True)
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    print(f"✅ 已部署到 https://guoguo99.xyz/{files[0]}")
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='抖音跳转卡片批量生成器')
    parser.add_argument('--title', default='免费领取实操资料', help='卡片标题')
    parser.add_argument('--desc', default='点击领取，限时免费', help='卡片描述')
    parser.add_argument('--url', default='https://guoguo99.xyz', help='跳转目标URL')
    parser.add_argument('--filename', required=True, help='输出文件名，如 card-001.html')
    parser.add_argument('--no-deploy', action='store_true', help='只生成不部署')
    args = parser.parse_args()
    
    html_file, png_file = generate_card(args.title, args.desc, args.url, args.filename)
    
    if not args.no_deploy:
        deploy([html_file, png_file])
