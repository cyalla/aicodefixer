# app/__init__.py
from flask import Flask
from app.github import github_bp

app = Flask(__name__)
app.register_blueprint(github_bp, url_prefix='/github')
