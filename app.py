from flask import Flask, render_template, request, jsonify
import sqlite3
import speech_recognition as sr
from datetime import datetime
import pytz
import os
from werkzeug.utils import secure_filename
from colorama import init, Fore

init(autoreset=True)  # Инициализация colorama

app = Flask(__name__)
app.config['DATABASE'] = 'instance/obscene_words.db'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Папка для временных аудиофайлов

# Создание папки для загрузки, если она отсутствует
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify(success=False, error="Файл не получен.")

    audio_file = request.files['audio']
    filename = secure_filename(audio_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(file_path)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            print(Fore.GREEN + "Распознанный текст:", text)

            # Проверка на наличие мата
            obscene_words = ["слово1", "слово2"]  # Ваш список матов
            detected_words = [word for word in obscene_words if word in text.lower()]

            os.remove(file_path)  # Удаляем временный файл

            if detected_words:
                save_to_db(detected_words)
                return jsonify(success=True, message=f"Обнаружены маты: {', '.join(detected_words)}")
            else:
                return jsonify(success=True, message="Маты не обнаружены.")

    except sr.UnknownValueError:
        return jsonify(success=False, error="Не удалось распознать речь.")
    except Exception as e:
        return jsonify(success=False, error=str(e))

def save_to_db(words):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    moscow_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
    for word in words:
        cursor.execute("INSERT INTO bad_words (word, timestamp) VALUES (?, ?)", (word, moscow_time))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
