from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import os
import json
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# File paths for our JSON storage
VIDEOS_FILE = 'data/videos.json'
SUBSCRIBERS_FILE = 'data/subscribers.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

def load_json_file(filepath: str) -> List[Dict]:
    """Load data from a JSON file. If file doesn't exist, return empty list."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json_file(filepath: str, data: List[Dict]):
    """Save data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# Video functions
def get_all_videos():
    return load_json_file(VIDEOS_FILE)

def add_video(caption: str, video_url: str):
    videos = get_all_videos()
    # Generate a new ID
    new_id = max([video.get('id', 0) for video in videos], default=0) + 1
    videos.append({
        'id': new_id,
        'caption': caption,
        'video_url': video_url
    })
    save_json_file(VIDEOS_FILE, videos)

def delete_video(video_id: int):
    videos = get_all_videos()
    videos = [v for v in videos if v.get('id') != video_id]
    save_json_file(VIDEOS_FILE, videos)

# Subscriber functions
def get_all_subscribers():
    return load_json_file(SUBSCRIBERS_FILE)

def add_subscriber(email: str) -> bool:
    subscribers = get_all_subscribers()
    # Check if email already exists
    if any(sub['email'] == email for sub in subscribers):
        return False
    
    subscribers.append({
        'id': len(subscribers) + 1,
        'email': email
    })
    save_json_file(SUBSCRIBERS_FILE, subscribers)
    return True

@app.route('/')
def index():
    videos = get_all_videos()
    return render_template('index.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == os.getenv('USERNAME') and password == os.getenv('PASSWORD'):
            session['user_id'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('add_video_route'))  # Changed from 'add_video' to 'add_video_route'
        else:
            flash('Login failed. Check your username and/or password.', 'error')

    return render_template('login.html')

@app.route('/add_video', methods=['GET', 'POST'])
def add_video_route():
    if 'user_id' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'add_video' in request.form:
            caption = request.form['caption']
            video_url = request.form['video_url']
            add_video(caption, video_url)
            flash('Video added successfully!', 'success')

        elif 'delete_video' in request.form:
            video_id = int(request.form['video_id'])
            delete_video(video_id)
            flash('Video deleted successfully!', 'success')

        return redirect(url_for('add_video_route'))

    videos = get_all_videos()
    return render_template('add_video.html', videos=videos)

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        if add_subscriber(email):
            flash(f'Successfully subscribed {email} to the email list!', 'success')
        else:
            flash('This email is already subscribed!', 'error')
        return redirect(url_for('index'))

    return render_template('subscribe.html')

@app.route('/subscribers')
def show_subscribers():
    subscribers = get_all_subscribers()
    emails = [sub['email'] for sub in subscribers]
    return render_template('subscribers.html', emails=emails)

if __name__ == '__main__':
    app.run()
