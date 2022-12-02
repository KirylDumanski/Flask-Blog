from flask import Flask, render_template, request, flash, session, redirect, url_for, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aSDSfg__31f^%^&dfdTT>|21dhjkdf%^*=--0234ksldfn'

menu = [{"name": "Install", "url": "install-flask"},
        {"name": "First app", "url": "first-app"},
        {"name": "Feedback", "url": "feedback"}]


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html', title='Main page!', menu=menu)


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
