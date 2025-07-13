import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from .config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

from .file_systems.hadoop_client import HDFSManager
from .file_systems.file_client import FileManager


app = Flask(__name__)
app.config.from_object(Config)

# Logging
if not os.path.exists(Config.LOG_DIRECTORY):
    os.mkdir(Config.LOG_DIRECTORY)
for handler in list(app.logger.handlers):
    app.logger.removeHandler(handler)
file_handler = RotatingFileHandler(os.path.join(Config.LOG_DIRECTORY, 'app.log'), maxBytes=1_048_576, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
app.logger.addHandler(stdout_handler)

app.logger.info(' | INIT | Document Manager startup')
app.logger.info(f' | INIT | Creating base directories')
if not os.path.exists(Config.TMP_FOLDER):
    os.mkdir(Config.TMP_FOLDER)
    app.logger.info(f' | INIT | Created temporary folder: {Config.TMP_FOLDER}')
if not os.path.exists(Config.STATIC_FOLDER):
    os.mkdir(Config.STATIC_FOLDER)
    app.logger.info(f' | INIT | Created static folder: {Config.STATIC_FOLDER}')


db = SQLAlchemy()
ma = Marshmallow()

if Config.HADOOP:
    file_manager = HDFSManager(namenode_url=Config.HADOOP_NAMENODE_URL, user=Config.HADOOP_USERNAME)
else:
    file_manager = FileManager()

try:
    file_manager.create_directory(path=Config.PARENT_FOLDER)
except Exception as e:
    app.logger.error(f' | INIT | Error creating parent folder in file manager: {e}')
    raise e
db.init_app(app)
app.logger.info(' | INIT | Initialized SQLAlchemy database')
ma.init_app(app)
app.logger.info(' | INIT | Initialized Marshmallow')

from .routes.pdfs import pdf_bp
from .routes.attachments import attachment_bp

app.register_blueprint(pdf_bp, url_prefix='/api/pdfs')
app.logger.info(' | INIT | Registered blueprint: pdf_bp with prefix /api/pdfs')
app.register_blueprint(attachment_bp, url_prefix='/api/attachments')
app.logger.info(' | INIT | Registered blueprint: attachment_bp with prefix /api/attachments')

with app.app_context():
    db.create_all()
    app.logger.info(' | INIT | Created all database tables')

from .routes.ui import ui_bp
app.register_blueprint(ui_bp)
app.logger.info(' | INIT | Registered blueprint: ui_bp')
