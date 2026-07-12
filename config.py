import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "studentproductivitysecret"

    SQLALCHEMY_DATABASE_URI = "sqlite:///students.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False