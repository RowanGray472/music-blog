from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///local.db')

print("DATABASE_URL:", os.getenv('DATABASE_URL'))

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Use secret key from .env file
db = SQLAlchemy(app)

# Define the Video model
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(120), nullable=False)
    video_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Video {self.caption}>'

# Define the Subscriber model to store email addresses
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Subscriber {self.email}>'

@app.route('/')
def index():
    videos = Video.query.all()  # Retrieve all video records from the database
    return render_template('index.html', videos=videos)


# Simple login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Compare entered credentials with stored credentials from the .env file
        if username == os.getenv('USERNAME') and password == os.getenv('PASSWORD'):
            session['user_id'] = username  # Store the session
            flash('Logged in successfully!', 'success')
            return redirect(url_for('add_video'))  # Redirect to the add_video page
        else:
            flash('Login failed. Check your username and/or password.', 'error')

    return render_template('login.html')

# Add or Delete Video page
@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    # Check if the user is logged in by checking the session
    if 'user_id' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    if request.method == 'POST':
        if 'add_video' in request.form:
            # Add video
            caption = request.form['caption']
            video_url = request.form['video_url']
            
            new_video = Video(caption=caption, video_url=video_url)
            db.session.add(new_video)
            db.session.commit()

            flash('Video added successfully!', 'success')

        elif 'delete_video' in request.form:
            # Delete video
            video_id = request.form['video_id']
            video = Video.query.get_or_404(video_id)
            db.session.delete(video)
            db.session.commit()

            flash('Video deleted successfully!', 'success')

        return redirect(url_for('add_video'))  # After action, reload the page

    # Fetch all videos for display and deletion
    videos = Video.query.all()
    return render_template('add_video.html', videos=videos)

# Subscribe route
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if the email is already in the database
        existing_subscriber = Subscriber.query.filter_by(email=email).first()
        if existing_subscriber:
            flash('This email is already subscribed!', 'error')
        else:
            # Add new subscriber to the database
            new_subscriber = Subscriber(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash(f'Successfully subscribed {email} to the email list!', 'success')

        return redirect(url_for('index'))  # Redirect back to the index page

    return render_template('subscribe.html')

# Route to display all subscribers' emails
@app.route('/subscribers')
def show_subscribers():
    # Fetch all subscribers from the database
    subscribers = Subscriber.query.all()

    # Extract the email addresses for easy display
    emails = [subscriber.email for subscriber in subscribers]

    # Return the emails as a response (you can customize the display here)
    return render_template('subscribers.html', emails=emails)

if __name__ == '__main__':
    # Run the app and create tables on first run
    with app.app_context():
        db.create_all()
    app.run()

