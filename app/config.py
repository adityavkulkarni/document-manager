import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///document_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PARENT_FOLDER = os.getenv('PARENT_FOLDER', 'uploads')
    STATIC_FOLDER = os.path.join(os.getcwd(), "app", "static")
    TMP_FOLDER = os.path.join(os.getcwd(), os.getenv('TMP_FOLDER', 'tmp'))
    LOG_DIRECTORY = os.path.join(os.getcwd(), 'logs')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB limit
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    HADOOP = False
    HADOOP_NAMENODE_URL = os.getenv('HADOOP_NAMENODE_URL', None)
    HADOOP_USERNAME = os.getenv('HADOOP_USERNAME', None)
    if HADOOP_USERNAME is None or HADOOP_NAMENODE_URL is None:
        HADOOP = False
