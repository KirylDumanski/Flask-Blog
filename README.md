# Welcome to my Flask-Blog

## Introduction
"Flask-blog" is an application based on Python using the Flask microframework.

## Technology stack
* Python 3.8
* Flask
* SQLAlchemy ORM
* Flask-login
* Bootstrap 5

## Installation Guide
1. Clone git repository:
```
git clone https://github.com/KirylDumanski/Flask-site.git
```
2. Install a Virtual Environment.
3. Install the dependencies.
```
pip install -r requirements.txt  
```
4. Set the app package as the place where Flask should look for the create_app() factory function:
```
export FLASK_APP=app
```
5. Open the Flask shell to create DB:
```
flask shell
```
```
from app.models import Post, User, Profile
```
```
db.create_all()
```
6. Exit the flask shell `Ctrl+Z`,`Enter`
7. Run the application:
```
flask run
```