from flask import Flask, render_template, request, redirect, url_for, flash, g
from datetime import datetime
from models import db, User, Message, Workout  # Import the models

def create_app():
    app = Flask(__name__)
    app.secret_key = "abcd@1234"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Panda#2001@localhost:3306/fitness_center"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from services.user_management.user import user_bp
    app.register_blueprint(user_bp)
    from services.admin.memberships import memberships_bp
    app.register_blueprint(memberships_bp)

    return app

app = create_app()

@app.before_request
def load_user():
    g.user = {'workouts': ['Workout1', 'Workout2']}

@app.context_processor
def inject_user():
    return {'user': g.user}

@app.route('/')
def signin():
    return render_template("signin.html")

@app.route('/home')
def Home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/workout')
def workout():
    # Get current time in UTC
    utc_time = datetime.utcnow()
    current_datetime = utc_time.strftime('%Y-%m-%d %H:%M:%S')

    current_day = utc_time.strftime('%A')
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    suggested_workout_plan = {
        'Monday': ['Chest Press - 3 sets of 12 reps', 'Incline Dumbbell Press - 3 sets of 12 reps', 'Cable Fly - 3 sets of 15 reps', 'Push-ups - 3 sets of 20 reps', 'Tricep Dips - 3 sets of 15 reps'],
        'Tuesday': ['Pull-Ups - 3 sets of 10 reps', 'Lat Pulldowns - 3 sets of 12 reps', 'Seated Row - 3 sets of 12 reps', 'Barbell Curl - 3 sets of 15 reps', 'Hammer Curl - 3 sets of 15 reps'],
        'Wednesday': ['Squats - 3 sets of 12 reps', 'Lunges - 3 sets of 12 reps', 'Leg Press - 3 sets of 15 reps', 'Calf Raises - 3 sets of 20 reps', 'Leg Curl - 3 sets of 12 reps'],
        'Thursday': ['Shoulder Press - 3 sets of 12 reps', 'Lateral Raise - 3 sets of 15 reps', 'Front Raise - 3 sets of 15 reps', 'Shrugs - 3 sets of 15 reps', 'Reverse Fly - 3 sets of 15 reps'],
        'Friday': ['Deadlifts - 3 sets of 12 reps', 'Bent Over Row - 3 sets of 12 reps', 'T-Bar Row - 3 sets of 12 reps', 'Face Pulls - 3 sets of 15 reps', 'Rear Delt Fly - 3 sets of 15 reps'],
        'Saturday': ['Bench Press - 3 sets of 12 reps', 'Dumbbell Fly - 3 sets of 15 reps', 'Chest Dips - 3 sets of 15 reps', 'Skull Crushers - 3 sets of 15 reps', 'Tricep Kickback - 3 sets of 15 reps'],
        'Sunday': ['Rest Day']
    }

    return render_template('workout.html', current_datetime=current_datetime, current_day=current_day, days=days, suggested_workout_plan=suggested_workout_plan)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gym_tour')
def gym_tour():
    gallery_items = [
        {"src": "images/gym1.jpg", "alt": "Gym Image 1"},
        {"src": "images/gym2.jpg", "alt": "Gym Image 2"},
        {"src": "images/gym3.jpg", "alt": "Gym Image 3"},
        {"src": "images/gym4.jpg", "alt": "Gym Image 4"},
        {"src": "images/gym5.jpg", "alt": "Gym Image 5"},
        {"src": "images/gym6.jpg", "alt": "Gym Image 6"},
        {"src": "images/gym7.jpg", "alt": "Gym Image 7"},
        {"src": "images/gym8.jpg", "alt": "Gym Image 8"},
        {"src": "images/gym9.jpg", "alt": "Gym Image 9"},
        {"src": "images/gym10.jpg", "alt": "Gym Image 10"},
        {"src": "images/gym11.jpg", "alt": "Gym Image 11"},
        {"src": "images/gym12.jpg", "alt": "Gym Image 12"},
        {"src": "images/gym13.jpg", "alt": "Gym Image 13"},
        {"src": "images/gym14.jpg", "alt": "Gym Image 14"},
        {"src": "images/gym15.jpg", "alt": "Gym Image 15"},
        {"src": "images/gym16.jpg", "alt": "Gym Image 16"},
        {"src": "images/gym17.jpg", "alt": "Gym Image 17"},
        {"src": "images/gym18.jpg", "alt": "Gym Image 18"},
        {"src": "images/gym19.jpg", "alt": "Gym Image 19"},
        {"src": "images/gym20.jpg", "alt": "Gym Image 20"},
    ]
    return render_template('gym_tour.html', gallery_items=gallery_items)

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    # Create a new Message object and save it to the database
    new_message = Message(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()
    
    flash('Your message has been sent successfully!', 'success')
    return redirect(url_for('contact'))

@app.route('/save_workout', methods=['POST'])
def save_workout():
    user_id = 1  # Replace with the actual user ID
    workout_data = request.form['workout_data']
    
    # Create a new Workout object and save it to the database
    new_workout = Workout(user_id=user_id, workout_data=workout_data)
    db.session.add(new_workout)
    db.session.commit()
    
    flash('Your workout has been saved successfully!', 'success')
    return redirect(url_for('workout'))

@app.route('/process_signin', methods=['POST'])
def process_signin():
    username = request.form['username']
    password = request.form['password']
    if username == "admin" and password == "password":
        flash('Sign in successful!', 'success')
        return redirect(url_for('workout'))
    else:
        flash('Invalid username or password', 'danger')
        return redirect(url_for('signin'))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
