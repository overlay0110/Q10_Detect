import subprocess
import os
import sys
from flask import Flask, request, jsonify, render_template
from pyfladesk import init_gui

def file_content(filename):
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    path = scriptDir + os.path.sep + filename

    result = ''
    read_offset = open(path, mode='r', encoding='utf-8')
    lines = read_offset.readlines()
    for line in lines:
        result += line
    read_offset.close()
    return result

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def log_filter(logs):
    result = []
    
    r = logs.split('\n')
    for l in r:
        result.append(l.split('\t'))
    return result

def get_log():
    logs = log_filter(file_content("log\\log1.txt"))
    logs.reverse()
    count = len(logs)
    logs = enumerate(logs)
    logstr = ''
    for i, d in logs:
        log = ''
        for index,w in enumerate(d):
            if index < 2:
                log += w + ' '
        logstr += str(count-i-1) + '. ' + log + '\n'
    return logstr

def find_log(findValue):
    logs = log_filter(file_content("log\\log1.txt"))
    for d in logs:
        for w in d:
            if w == findValue:
                return True
    return False

if getattr(sys, 'frozen', False):
    template_folder = resource_path('templates')
    static_folder = resource_path('static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

@app.route("/")
def main():
    logstr = get_log()
    return render_template("index.html", datas=logstr)

@app.route("/add_log", methods=['POST'])
def add_log():
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    path = scriptDir + os.path.sep + 'check-win.exe'

    values = request.form

    serial = values.get('serial')

    if find_log(serial):
        response = {'result': 'f', 'msg' : '이미 등록된 시리얼번호입니다. 확인 후 다시 입력해주세요.'}
        return jsonify(response), 200

    o, e = subprocess.Popen([ path, serial ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if o:
        print(o)
        response = {'result': 'f', 'msg' : '이미 등록된 기기입니다. 다른 기기를 연결해주세요.'}
        return jsonify(response), 200
    
    if e:
        print(e)
        response = {'result': 'f', 'msg' : '기기와 연결이 실패했습니다. 다시 연결해주세요.'}
        return jsonify(response), 200

    response = {'result': 'success', 'datas' : 'test'}
    return jsonify(response), 200
    
@app.route("/get_logs", methods=['POST'])
def get_logs():
    temp = get_log()
    response = {'result': 'success', 'logs' : temp}
    return jsonify(response), 200

if __name__ == '__main__':
    init_gui(app, port=5115, width=1200, height=600)
    app.run()