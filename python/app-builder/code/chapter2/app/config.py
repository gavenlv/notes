import os
from flask_appbuilder.security.manager import AUTH_DB

# Your App Name
APP_NAME = "Chapter 2 App - Models and Database"

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Authentication Configuration
AUTH_TYPE = AUTH_DB  # Database authentication

# Theme Configuration
APP_THEME = ""  # default theme