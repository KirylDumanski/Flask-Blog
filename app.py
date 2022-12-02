from flask import Flask, render_template

app = Flask(__name__)

menu = [{"name": "Install", "url": "install-flask"},
        {"name": "First app", "url": "first-app"},
        {"name": "Feedback", "url": "feedback"}]


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html', title='Main page!', menu=menu)


@app.route("/feedback")
def feedback():
    return render_template('feedback.html', title="Feedback!", menu=menu)


if __name__ == '__main__':
    app.run(debug=True)
