from datetime import datetime

from flask import Flask, render_template, request, flash, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy

SECRET_KEY = 'development_key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///flask-site.db'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

menu = [{"name": "Main page", "url": "index"},
        {"name": "Add post", "url": "add-post"},
        {"name": "Feedback", "url": "feedback"},
        {"name": "Login", "url": "login"}]


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Article {self.id}>"


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html', title='Main page', menu=menu)


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if len(request.form['username']) > 3:
            flash('Message sent', category='success')
        else:
            flash('Sending error', category='error')
    return render_template('feedback.html', title="Feedback!", menu=menu)


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == "POST" and request.form['username'] == 'Admin' and request.form['password'] == 'admin':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Authorization', menu=menu)


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"{username}'s profile."


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Page not found', menu=menu), 404


if __name__ == '__main__':
    app.run(debug=True)
