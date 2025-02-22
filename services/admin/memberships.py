from flask import Blueprint, render_template, request, jsonify, redirect, url_for,session
from app import db
from sqlalchemy.exc import SQLAlchemyError

from services.user_management.user import User

class Membership(db.Model):
    __tablename__ = "memberships"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Membership plan name
    price = db.Column(db.Float, nullable=False)       # Price per month
    description = db.Column(db.Text, nullable=False)  # Description of the plan

    def __init__(self, name, price, description):
        self.name = name
        self.price = price
        self.description = description


from datetime import datetime, timedelta


class UserMembership(db.Model):
    __tablename__ = "user_memberships"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Link to User table
    membership_id = db.Column(db.Integer, db.ForeignKey("memberships.id"), nullable=False)  # Link to Membership table
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Membership start date
    expiry_date = db.Column(db.DateTime, nullable=False)  # Membership expiry date
    is_active = db.Column(db.Boolean, default=False, nullable=False)  # Whether the membership is active or not

    # Relationships (optional)
    user = db.relationship("User", backref="memberships")
    membership = db.relationship("Membership", backref="user_memberships")

    def __init__(self, user_id, membership_id, duration_months=1):
        self.user_id = user_id
        self.membership_id = membership_id
        self.start_date = datetime.utcnow()
        self.expiry_date = self.start_date + timedelta(days=30 * duration_months)


memberships_bp = Blueprint("memberships", __name__, url_prefix="/memberships", template_folder="templates", static_folder="static")

@memberships_bp.route("/")
def membership():
    print(session.get("id"))
    return render_template("memberships.html")

@memberships_bp.route("/create", methods=["POST"])
def createNewMembership():
    try:
        # Get data from the request JSON payload
        data = request.get_json()

        # Extract fields from the JSON payload
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        

        # Validate the input fields
        if not all([name, description, price]):
            return jsonify({"error": "All fields (name, description, price,  ) are required"}), 400

        # Convert price and   to appropriate types
        try:
            price = float(price)
        except ValueError:
            return jsonify({"error": "Price must be a number and  must be an integer"}), 400

        # Create a new Membership object
        new_membership = Membership(
            name=name,
            description=description,
            price=price,
            
        )
        print(new_membership)
        # Add and commit the new membership to the database
        db.session.add(new_membership)
        db.session.commit()

        # Return a success response
        return jsonify({"message": "New membership created successfully", "membership_id": new_membership.id}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"errorl": str(e)}), 500

    except Exception as e:
        print(e)
        return jsonify({"errorg": str(e)}), 500
    
    
@memberships_bp.route("/user_memberships", methods=["GET"])
def view_user_memberships():
    user_memberships = UserMembership.query.all()
    return render_template("user_memberships.html", user_memberships=user_memberships)

@memberships_bp.route("/user_memberships/add", methods=["GET", "POST"])
def add_user_membership():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        membership_id = request.form.get("membership_id")
        duration_months = int(request.form.get("duration_months", 1))

        if not user_id or not membership_id:
            return jsonify({"error": "User and Membership fields are required"}), 400

        try:
            existing_membership = UserMembership.query.filter_by(user_id=user_id, is_active=True).first()
            if existing_membership:
                return jsonify({"error": "User already has an active membership"}), 400

            user_membership = UserMembership(user_id=user_id, membership_id=membership_id, duration_months=duration_months)
            db.session.add(user_membership)
            db.session.commit()
            # return redirect(url_for("memberships.view_user_memberships"))
            return jsonify({"msg": "success added membership"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    users = User.query.all()
    memberships = Membership.query.all()
    return render_template("add_user_membership.html", users=users, memberships=memberships)

@memberships_bp.route("/payment", methods=["POST", "GET"])
def payment():
    if request.method == "GET":
        return render_template("payment_page.html")
    try:
        # Extract data from the form
        user_id = session.get("id")
        membership_id = request.form.get("membership_id")
        total_amount = request.form.get("total_amount")
        print( "amount ", total_amount)
        # Check if all required data is present
        if not all([user_id, membership_id, total_amount]):
            return jsonify({"error": "User ID, Membership ID, and Total Amount are required"}), 400

        # Optionally, validate if the user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Optionally, check if the membership exists
        membership = Membership.query.get(membership_id)
        if not membership:
            return jsonify({"error": "Membership not found"}), 404

        # Create UserMembership instance
        user_membership = UserMembership(
            user_id=user_id,
            membership_id=membership_id,
            duration_months=1  # Assuming it's always 1 month for simplicity; you can adjust as necessary
        )
        db.session.add(user_membership)
        db.session.commit()

        # Redirect or return success message
        return redirect(url_for('memberships.payment_page', membership_id=membership_id, total_amount=total_amount, user_id=user_id))

    except Exception as e:
        db.session.rollback()
        return jsonify({"errorg": str(e)}), 500

@memberships_bp.route('/payment_page')
def payment_page():
    payload = dict()
    
    payload['membership_id'] = request.args.get('membership_id')
    payload['total_amount'] = request.args.get('total_amount')
    payload['user_id'] = request.args.get('user_id')
    return render_template("payment_page.html", payload=payload)
