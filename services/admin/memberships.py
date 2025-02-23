from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.models import db, User, Membership, UserMembership  # Import models
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

memberships_bp = Blueprint("memberships", __name__, url_prefix="/memberships", template_folder="templates", static_folder="static")

@memberships_bp.route("/")
def membership():
    print(session.get("id"))
    return render_template("memberships.html")

@memberships_bp.route("/create", methods=["POST"])
def createNewMembership():
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        
        if not all([name, description, price]):
            return jsonify({"error": "All fields (name, description, price) are required"}), 400
        
        try:
            price = float(price)
        except ValueError:
            return jsonify({"error": "Price must be a number"}), 400
        
        new_membership = Membership(name=name, description=description, price=price)
        db.session.add(new_membership)
        db.session.commit()
        return jsonify({"message": "New membership created successfully", "membership_id": new_membership.id}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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
        user_id = session.get("id")
        membership_id = request.form.get("membership_id")
        total_amount = request.form.get("total_amount")
        if not all([user_id, membership_id, total_amount]):
            return jsonify({"error": "User ID, Membership ID, and Total Amount are required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        membership = Membership.query.get(membership_id)
        if not membership:
            return jsonify({"error": "Membership not found"}), 404

        user_membership = UserMembership(user_id=user_id, membership_id=membership_id, duration_months=1)
        db.session.add(user_membership)
        db.session.commit()

        return redirect(url_for('memberships.payment_page', membership_id=membership_id, total_amount=total_amount, user_id=user_id))

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@memberships_bp.route('/payment_page')
def payment_page():
    payload = {
        'membership_id': request.args.get('membership_id'),
        'total_amount': request.args.get('total_amount'),
        'user_id': request.args.get('user_id')
    }
    return render_template("payment_page.html", payload=payload)
