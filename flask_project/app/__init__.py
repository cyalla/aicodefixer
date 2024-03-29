# app/__init__.py
from flask import Flask
from app.github import github_bp
from app.tomcatUtils import monitor_logs

#assuming the service is running on tomcat server
monitor_logs()

app = Flask(__name__)
app.register_blueprint(github_bp, url_prefix='/github')
