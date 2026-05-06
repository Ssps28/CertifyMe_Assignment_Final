import logging
import re
import secrets
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from models import db, Admin, Opportunity

main = Blueprint("main", __name__)

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

reset_tokens = {}


def success_response(data=None, status=200):
    response = {"status": "success"}
    if data:
        response.update(data)
    return jsonify(response), status


def error_response(message, status=400):
    return jsonify({
        "status": "error",
        "message": message
    }), status


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    return render_template("index.html")


@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not all([full_name, email, password, confirm_password]):
        return error_response("All fields are required.")

    if not EMAIL_REGEX.match(email):
        return error_response("Invalid email format.")

    if len(password) < 8:
        return error_response(
            "Password must be at least 8 characters."
        )

    if password != confirm_password:
        return error_response("Passwords do not match.")

    existing_admin = Admin.query.filter_by(email=email).first()

    if existing_admin:
        return error_response(
            "An account with this email already exists."
        )

    admin = Admin(
        full_name=full_name,
        email=email
    )

    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    return success_response({
        "message": "Account created successfully."
    }, 201)


@main.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember_me = bool(data.get("remember_me", False))

    admin = Admin.query.filter_by(email=email).first()

    if not admin or not admin.check_password(password):
        return error_response(
            "Invalid email or password",
            401
        )

    login_user(admin, remember=remember_me)

    if remember_me:
        session.permanent = True

    return success_response({
        "message": "Login successful",
        "redirect": "/dashboard"
    })


@main.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()

    return success_response({
        "message": "Logged out successfully"
    })


@main.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()

    admin = Admin.query.filter_by(email=email).first()

    if admin:
        token = secrets.token_urlsafe(32)

        expires_at = datetime.utcnow() + timedelta(
            seconds=current_app.config[
                "RESET_TOKEN_EXPIRY_SECONDS"
            ]
        )

        reset_tokens[token] = {
            "admin_id": admin.id,
            "expires_at": expires_at
        }

        reset_link = url_for(
            "main.reset_password_page",
            token=token,
            _external=True
        )

        print("\nPASSWORD RESET LINK:")
        print(reset_link)
        print()

    return success_response({
        "message": (
            "If the email exists, a reset link has been generated."
        )
    })


@main.route("/reset-password/<token>")
def reset_password_page(token):
    token_data = reset_tokens.get(token)

    if (
        not token_data or
        datetime.utcnow() > token_data["expires_at"]
    ):
        return "Reset link expired or invalid", 400

    return render_template("index.html")


def validate_opportunity_data(data):
    required_fields = [
        "name",
        "duration",
        "start_date",
        "description",
        "skills",
        "category",
        "future_opportunities"
    ]

    for field in required_fields:
        if not (data.get(field) or "").strip():
            return f"{field.replace('_', ' ').title()} is required."

    return None


@main.route("/api/opportunities", methods=["GET"])
@login_required
def get_opportunities():
    opportunities = Opportunity.query.filter_by(
        admin_id=current_user.id
    ).all()

    return success_response({
        "data": [item.to_dict() for item in opportunities]
    })


@main.route("/api/opportunities", methods=["POST"])
@login_required
def create_opportunity():
    data = request.get_json(silent=True) or {}

    validation_error = validate_opportunity_data(data)

    if validation_error:
        return error_response(validation_error)

    opportunity = Opportunity(
        name=data["name"],
        duration=data["duration"],
        start_date=data["start_date"],
        description=data["description"],
        skills=data["skills"],
        category=data["category"],
        future_opportunities=data["future_opportunities"],
        max_applicants=data.get("max_applicants"),
        admin_id=current_user.id
    )

    db.session.add(opportunity)
    db.session.commit()

    return success_response({
        "message": "Opportunity created successfully",
        "data": opportunity.to_dict()
    }, 201)


@main.route("/api/opportunities/<int:opportunity_id>", methods=["GET"])
@login_required
def get_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)

    if opportunity.admin_id != current_user.id:
        return error_response(
            "Unauthorized access",
            403
        )

    return success_response({
        "data": opportunity.to_dict()
    })


@main.route("/api/opportunities/<int:opportunity_id>", methods=["PUT"])
@login_required
def update_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)

    if opportunity.admin_id != current_user.id:
        return error_response(
            "Unauthorized access",
            403
        )

    data = request.get_json(silent=True) or {}

    validation_error = validate_opportunity_data(data)

    if validation_error:
        return error_response(validation_error)

    opportunity.name = data["name"]
    opportunity.duration = data["duration"]
    opportunity.start_date = data["start_date"]
    opportunity.description = data["description"]
    opportunity.skills = data["skills"]
    opportunity.category = data["category"]
    opportunity.future_opportunities = data["future_opportunities"]
    opportunity.max_applicants = data.get("max_applicants")

    db.session.commit()

    return success_response({
        "message": "Opportunity updated successfully",
        "data": opportunity.to_dict()
    })


@main.route("/api/opportunities/<int:opportunity_id>", methods=["DELETE"])
@login_required
def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)

    if opportunity.admin_id != current_user.id:
        return error_response(
            "Unauthorized access",
            403
        )

    db.session.delete(opportunity)
    db.session.commit()

    return success_response({
        "message": "Opportunity deleted successfully"
    })