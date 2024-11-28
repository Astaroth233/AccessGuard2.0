import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import random
import base64
from utils.encryption import encrypt_data, decrypt_data
from utils.face_recognition import capture_face_data
from utils.voice_recognition import capture_voice_data
from datetime import datetime

app = Flask(__name__)

# Set up logging
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file = os.path.join(log_directory, 'app.log')

logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['user_database']
collection = db['user_data']

def generate_unique_user_id():
    while True:
        user_id = str(random.randint(1000000, 9999999))  # Generate a 7-digit user ID
        if not collection.find_one({'user_id': user_id}):
            return user_id

def create_log_entry(event, user_id, details=""):
    log_message = f"Event: {event}, User ID: {user_id}, Details: {details}"
    logging.info(log_message)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store', methods=['GET', 'POST'])
def store():
    if request.method == 'POST':
        name = request.form['name']
        rollno = request.form['rollno']
        semester = request.form['semester']
        face_data = request.form['face_data']
        voice_data = request.form['voice_data']
        
        user_id = generate_unique_user_id()  # Generate a unique 7-digit user ID

        # Save face and voice data to files
        face_filename = f"data/{user_id}.jpg"
        voice_filename = f"data/{user_id}.wav"
        with open(face_filename, 'wb') as f:
            f.write(base64.b64decode(face_data))
        with open(voice_filename, 'wb') as f:
            f.write(base64.b64decode(voice_data))
        
        encrypted_face_data = encrypt_data(face_filename)
        encrypted_voice_data = encrypt_data(voice_filename)
        
        user_data = {
            'user_id': user_id,
            'name': name,
            'rollno': rollno,
            'semester': semester,
            'face_data': encrypted_face_data,
            'voice_data': encrypted_voice_data
        }
        
        collection.insert_one(user_data)
        create_log_entry("Registration", user_id, f"User {name} registered with roll number {rollno}")

        print(f"Stored User ID: {user_id}")
        print(f"Stored Face Data Base64: {face_data}")
        print(f"Stored Voice Data Base64: {voice_data}")
        
        return redirect(url_for('welcome', user_id=user_id, name=name, rollno=rollno))
    return render_template('store.html')

@app.route('/recognize', methods=['GET', 'POST'])
def recognize():
    if request.method == 'POST':
        user_id = request.form['user_id']
        face_data = request.form['face_data']
        voice_data = request.form['voice_data']
        
        user = collection.find_one({'user_id': user_id})
        
        if user:
            encrypted_face_data = user['face_data']
            encrypted_voice_data = user['voice_data']
            face_filename = decrypt_data(encrypted_face_data)
            voice_filename = decrypt_data(encrypted_voice_data)
            
            stored_face_data = open(face_filename, 'rb').read()
            stored_voice_data = open(voice_filename, 'rb').read()
            
            print(f"Retrieved Face Data Base64: {base64.b64encode(stored_face_data).decode('utf-8')}")
            print(f"Retrieved Voice Data Base64: {base64.b64encode(stored_voice_data).decode('utf-8')}")
            
            if base64.b64encode(stored_face_data).decode('utf-8') != face_data:
                create_log_entry("Unauthorized Entry Attempt", user_id, "Face data does not match")
                return "Face data does not match. Unauthorized entry, Please register"
            elif base64.b64encode(stored_voice_data).decode('utf-8') != voice_data:
                create_log_entry("Unauthorized Entry Attempt", user_id, "Voice data does not match")
                return "Voice data does not match. Unauthorized entry, Please register"
            else:
                create_log_entry("Successful Entry", user_id, "User successfully recognized")
                return redirect(url_for('welcome', user_id=user_id, name=user['name'], rollno=user['rollno']))
        else:
            create_log_entry("Unauthorized Entry Attempt", user_id, "User ID not found")
            return "User ID not found. Please register"
    return render_template('recognize.html')

@app.route('/welcome')
def welcome():
    user_id = request.args.get('user_id')
    name = request.args.get('name')
    rollno = request.args.get('rollno')
    return render_template('welcome.html', user_id=user_id, name=name, rollno=rollno)

@app.route('/capture_face_data', methods=['GET'])
def capture_face():
    face_img = capture_face_data()
    if face_img:
        return jsonify({'success': True, 'face_data': face_img})
    return jsonify({'success': False})

@app.route('/capture_voice_data', methods=['GET'])
def capture_voice():
    voice_data = capture_voice_data()
    if voice_data:
        with open('data/temp.wav', 'rb') as f:
            voice_data = f.read()
        return jsonify({'success': True, 'voice_data': base64.b64encode(voice_data).decode('utf-8')})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)
