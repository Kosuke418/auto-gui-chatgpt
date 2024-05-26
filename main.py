import tkinter as tk
import openai
import pyautogui
from dotenv import load_dotenv
import os
import json
import re
import subprocess

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
openai.api_key = os.getenv('OPENAI_API_KEY')

# キャッシュファイルのパス
CACHE_FILE = 'command_cache.json'
# 履歴ファイルのパス
HISTORY_FILE = 'command_history.json'

# キャッシュを読み込む
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        command_cache = json.load(f)
else:
    command_cache = {}

# 履歴を読み込む
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        command_history = json.load(f)
else:
    command_history = []

def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(command_cache, f)

def save_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump(command_history, f)

def get_command_from_chatgpt(user_input):
    # 以前の命令があればそれを追加してコマンドを生成する
    messages = [{"role": "system", "content": "You are a helpful assistant that converts natural language commands into PyAutoGUI commands for windows."}]
    for command in command_history:
        messages.append({"role": "user", "content": f"次の命令をPyAutoGUIのコードに変換してください: {command['input']}"})
        messages.append({"role": "assistant", "content": command['command']})
    messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that converts natural language commands into PyAutoGUI commands for windows."},
                {"role": "user", "content": f"次の命令をPyAutoGUIのコードに変換してください: {user_input}"}
            ],
            max_tokens=100
        )
        command = response.choices[0].message['content'].strip()

        # Pythonコードブロックのみを抽出する
        code_match = re.search(r'```python(.*?)```', command, re.DOTALL)
        if code_match:
            command = code_match.group(1).strip()

        command_cache[user_input] = command
        save_cache()
        return command
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def execute_command(command):
    try:
        exec(command)
    except Exception as e:
        print(f"コマンドの実行中にエラーが発生しました: {e}")

def execute_app(app_name):
    try:
        subprocess.Popen(app_name)
    except Exception as e:
        print(f"アプリケーションの起動中にエラーが発生しました: {e}")

def process_command(event=None):
    user_input = entry.get()
    if user_input:
        command = get_command_from_chatgpt(user_input)
        execute_command(command)
        # 履歴に追加
        command_history.append({"input": user_input, "command": command})
        save_history()
        # テキストエントリーをクリア
        entry.delete(0, tk.END)
        # 履歴表示を更新
        update_history_display()

def update_history_display():
    # 履歴を表示するためのテキストウィジェットをクリア
    history_text.delete(1.0, tk.END)
    # 履歴を追加
    for command in command_history:
        history_text.insert(tk.END, f"{command['input']}\n{command['command']}\n\n")
    # 最後の履歴までスクロール
    history_text.see(tk.END)

# GUIのセットアップ
root = tk.Tk()
root.title("命令入力")

# ラベル
label = tk.Label(root, text="命令を入力してください:")
label.pack()

# テキストエントリー
entry = tk.Entry(root, width=50)
entry.pack()
entry.focus()  # エントリーにフォーカスを合わせる

# Enterキーが押されたときに命令を処理するようにバインドする
entry.bind("<Return>", process_command)

# 履歴表示用のテキストウィジェット
history_text = tk.Text(root, wrap=tk.WORD, width=60, height=20)
history_text.pack()

# 初期表示のために履歴を更新
update_history_display()

root.mainloop()
