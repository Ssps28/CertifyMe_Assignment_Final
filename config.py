import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "replace-this-with-a-secure-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "qatar_foundation.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

    RESET_TOKEN_EXPIRY_SECONDS = 3600

    ALLOWED_CATEGORIES = [
        "Technology",
        "Business",
        "Design",
        "Marketing",
        "Data Science",
        "Other"
    ]