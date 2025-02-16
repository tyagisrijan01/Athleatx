from flask import Flask, render_template, g
from app import db

def create_app():
    app = Flask(__name__)

    # Configure the app (replace with your actual database details)
    app.secret_key = "abcd@1234"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Panda#2001@localhost:3306/fitness_center"  # Ensure this is correct
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from services.user_management.user import user_bp  # Ensure this module exists and is correctly implemented
    app.register_blueprint(user_bp)
    from services.admin.memberships import memberships_bp
    app.register_blueprint(memberships_bp)

    return app

if __name__ == "__main__":
    app = create_app()

    @app.route('/')
    def init():
        # Mock user object for demonstration purposes
        user = {
            'workouts': []
        }
        return render_template("signin.html", user=user)

    # Ensure database tables are created before running the app
    with app.app_context():
        db.create_all()

    # Run the application
    app.run(debug=True)