import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "studentproductivitysecret"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "students.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False