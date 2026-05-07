from flask import Flask, jsonify, send_file
import os
import re

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_FOLDER = os.path.join(ROOT_DIR, 'data')


def scan_resources():
    """扫描 data 文件夹，解析所有资源"""
    resources = []
    
    if not os.path.exists(DATA_FOLDER):
        return resources
    
    folders = []
    for item in os.listdir(DATA_FOLDER):
        item_path = os.path.join(DATA_FOLDER, item)
        if os.path.isdir(item_path):
            folders.append(item)
    
    folders.sort(key=lambda f: os.path.getmtime(os.path.join(DATA_FOLDER, f)), reverse=True)
    
    for folder in folders:
        folder_path = os.path.join(DATA_FOLDER, folder)
        txt_file = os.path.join(folder_path, f"{folder}.txt")
        
        if os.path.exists(txt_file):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title = re.search(r'<Title>(.*?)<Title>', content, re.DOTALL)
                img1 = re.search(r'<img1>(.*?)<img1>', content, re.DOTALL)
                img2 = re.search(r'<img2>(.*?)<img2>', content, re.DOTALL)
                cont = re.search(r'<cont>(.*?)<cont>', content, re.DOTALL)
                download = re.search(r'<download>(.*?)<download>', content, re.DOTALL)
                
                if title:
                    resources.append({
                        'title': title.group(1).strip(),
                        'folder': folder,
                        'img1': f"{folder}/{img1.group(1).strip()}" if img1 else '',
                        'img2': f"{folder}/{img2.group(1).strip()}" if img2 else '',
                        'content': cont.group(1).strip() if cont else '',
                        'download': download.group(1).strip() if download else ''
                    })
            except Exception as e:
                print(f"解析 {txt_file} 出错: {e}")
    
    return resources


@app.route('/')
def index():
    return send_file(os.path.join(ROOT_DIR, 'index.html'))


@app.route('/api/resources')
def get_resources():
    return jsonify(scan_resources())


@app.route('/mainpage.png')
def mainpage():
    path = os.path.join(ROOT_DIR, 'mainpage.png')
    if os.path.exists(path):
        return send_file(path)
    return '', 404


@app.route('/data/<path:filename>')
def data_files(filename):
    return send_file(os.path.join(DATA_FOLDER, filename))


@app.route('/robots.txt')
def robots_txt():
    return """User-agent: *
Allow: /
""", 200, {'Content-Type': 'text/plain'}
