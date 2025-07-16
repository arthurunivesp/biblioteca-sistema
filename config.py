import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sala-de-leitura-chave-super-secreta-2024'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    BOOKS_PER_PAGE = 20
    LOANS_DURATION_DAYS = 14
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    