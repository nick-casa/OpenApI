import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///:memory:'
