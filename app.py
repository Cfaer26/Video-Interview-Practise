import os
import random
from flask import Flask, render_template, request, jsonify
import whisper
import cv2
import numpy as np

# Load Whisper model once at startup
whisper_model = whisper.load_model("base")

# Example questions
    # ... your questions here ...
COMMON_QUESTIONS = [
    "Tell me about yourself.",
    "Why are you interested in this position?",
    "Describe a time you worked in a team.",
    "What is your greatest strength?",
    "What is your greatest weakness?",
    "Why do you want to work at this company?",
    "Give an example of a time you showed leadership.",
    "Describe a challenge you faced and how you overcame it.",
    "Where do you see yourself in five years?",
    "Why should we hire you?",
    "Tell me about a time you worked on a team.",
    "Are you a team player? In what way?",
    "What role do you play on a team?",
    "Talk about a time in a group setting in which you took a leadership role",
    "How would you handle a disagreement with somebody else on my team?",
    "Describe a time you worked in a team and members of your team differed on the details and direction of a project. What did you do?",
    "What would you do in a situation where your teammate wasn't pulling their weight?",
    "Why do you want to work for __________[bank name]?",
    "Why do you want to work for ___________[division]?",
    "What do you think that our bank does differently than other firms?",
    "What is your understanding of the IBD division (or Markets division) and the analyst role?",
    "Tell me about a time that you had to make a very fast decision / split second decision",
    "Tell me about a time that you had to make a quick decision without full information",
    "Tell me about a time that you used technology to make a decision",
    "Tell me about a time you showed persistence / dealt with rejection",
    "Tell me about a time you failed and the lesson you learned from it.",
    "If you had a lot of things to do and not enough time to do them, what would you do?",
    "Tell me about a time that you acted with integrity",
    "What does integrity mean to you?",
    "How would other people describe your work ethic?",
    "What would you do if you saw someone cheating on a test?",
    "A student group president posts exam answers for all students in the group. How would you respond?",
    "What is a recent headline that you read in the news (e.g. the WSJ)?",
    "How do you follow the markets?",
    "Talk about how a major weather event would impact markets.",
    "What is an interesting article you read recently?",
    "How would you invest $1 million dollars?",
    "What asset classes are you following?",
    "Give me a pitch on something that you are passionate about (could be a stock, or a book, or TV show, etc.)",
    "Tell me about a time when you made a connection with a person from a different background",
    "Why did you choose your major, and do you think you made the right decision?",
    "Tell us a little bit about yourself and why it led you here."
]

app = Flask(__name__)

@app.route('/')
def index():
    question = random.choice(COMMON_QUESTIONS)
    return render_template('index.html', question=question)

@app.route('/next_question')
def next_question():
    question = random.choice(COMMON_QUESTIONS)
    return jsonify({'question': question})

@app.route('/upload', methods=['POST'])
def upload():
    video = request.files['video']
    video_path = os.path.join('uploads', video.filename)
    os.makedirs('uploads', exist_ok=True)
    video.save(video_path)

    # 1. Transcribe audio using Whisper
    transcript = transcribe_video(video_path)

    # 2. Analyze gaze using OpenCV (returns [0-10])
    gaze_score = analyze_gaze(video_path)

    # 3. Clarity score - simple heuristic (length, filler words, etc)
    clarity_score = analyze_clarity(transcript)

    overall_score = int((gaze_score + clarity_score) / 2)

    return jsonify({
        "transcript": transcript,
        "gaze_score": gaze_score,
        "clarity_score": clarity_score,
        "overall_score": overall_score
    })

def transcribe_video(video_path):
    import tempfile, subprocess
    with tempfile.NamedTemporaryFile(suffix=".wav") as wavfile:
        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-ar", "16000", "-ac", "1", "-f", "wav", wavfile.name
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = whisper_model.transcribe(wavfile.name)
    return result['text']

def analyze_gaze(video_path):
    cap = cv2.VideoCapture(video_path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    total, centered = 0, 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        total += 1
        for (x, y, w, h) in faces:
            cx = x + w // 2
            if abs(cx - frame.shape[1] // 2) < frame.shape[1] // 6:
                centered += 1
            break
    cap.release()
    if total == 0: return 0
    gaze_score = int(10 * centered / total)
    return gaze_score

def analyze_clarity(transcript):
    words = transcript.split()
    if not words:
        return 0
    filler_words = ['um', 'uh', 'like', 'you know', 'so']
    fillers = sum(word.lower() in filler_words for word in words)
    clarity = max(10 - fillers, 1)
    if len(words) < 50: clarity -= 2
    return max(clarity, 1)

if __name__ == '__main__':
    app.run(debug=True)
