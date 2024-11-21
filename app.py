from flask import Flask, jsonify, request, render_template
import speech_recognition as sr

app = Flask(__name__)

# Список запрещённых слов
obscene_words = {
    "tomato",  # Проверочное слово
    "badword2", "badword3",  # Английские
    "плохослово", "матерное",  # Русские
    "жамансөз", "боқтық"  # Казахские
}

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="ru-KZ,en-US")
        return text.lower()
    except sr.UnknownValueError:
        return "Не удалось распознать аудио."
    except sr.RequestError:
        return "Ошибка обработки аудио."

@app.route('/process-audio', methods=['POST'])
def process_audio():
    try:
        text = recognize_speech()
        if text in ["не удалось распознать аудио.", "ошибка обработки аудио."]:
            return jsonify(success=False, error=text)
        
        words = text.split()
        for word in words:
            if word in obscene_words:
                return jsonify(success=True, message=f"Мат обнаружен: {word}")
        
        return jsonify(success=True, message="Мат не обнаружен.")
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
