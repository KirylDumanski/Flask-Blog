from datetime import datetime

from flask import Flask, render_template, request, flash, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound, IntegrityError

SECRET_KEY = 'development_key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///flask-site.db'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

menu = [{"name": "Main page", "url": "index"},
        {"name": "Add post", "url": "add-post"},
        {"name": "Feedback", "url": "feedback"},
        {"name": "Login", "url": "login"}]


@app.context_processor
def inject_mainmenu():
    return dict(menu=menu)


@app.context_processor
def utility_processor():
    return dict(slugify=slugify)


@app.template_filter('iso_time')
def iso_time(s):
    return s.isoformat(' ', 'seconds')


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(150), unique=True, index=True)

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Article {self.id}>"


@app.route("/index")
@app.route("/")
def index():
    articles = Article.query.order_by(desc(Article.date)).all()
    return render_template('index.html', title='Main page', articles=articles)


@app.route("/post/<int:post_id>/<string:post_slug>")
def post_detail(post_id, post_slug):
    try:
        article = Article.query.filter_by(id=post_id, slug=post_slug).one()
    except NoResultFound:
        return render_template('page404.html', title='Page not found'), 404

    return render_template('post_detail.html', article=article, title=article.title)


@app.route("/post/delete/<int:post_id>")
def post_delete(post_id):
    article = Article.query.get_or_404(post_id)
    try:
        db.session.delete(article)
        db.session.commit()
        flash('Post successfully deleted!', category='success')
        return redirect(url_for('index'))
    except Exception as e:
        print(e)
        flash('An error occurred while deleting', category='error')
        return render_template(url_for('post_detail', post_id=article.id, post_slug=article.slug),
                               title='Add post')


@app.route("/post/update/<int:post_id>", methods=["GET", "POST"])
def post_update(post_id):
    article = Article.query.get_or_404(post_id)
    if request.method == 'POST':
        try:
            article.title = request.form['title']
            article.text = str(request.form['text'])
            article.slug = slugify(request.form['title'])
            db.session.commit()
            flash('Post updated', category='success')
            return render_template('update_post.html', article=article)
        except IntegrityError:
            db.session.rollback()
            flash('Update post error: Enter a unique post title!', category='error')

    return render_template('update_post.html', title='Update post', article=article)


@app.route("/add-post", methods=["POST", "GET"])
def add_post():
    if request.method == 'POST':
        try:
            article = Article(title=request.form['title'],
                              text=request.form['text'],
                              slug=slugify(request.form['title']))
            db.session.add(article)
            db.session.flush()
            flash('Post added', category='success')
        except:
            db.session.rollback()
            flash('Adding post error', category='error')
        else:
            db.session.commit()

    return render_template('add_post.html', title='Add post')


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if len(request.form['username']) > 3:
            flash('Message sent', category='success')
        else:
            flash('Sending error', category='error')
    return render_template('feedback.html', title="Feedback!")


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == "POST" and request.form['username'] == 'Admin' and request.form['password'] == 'admin':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Authorization')


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"{username}'s profile."


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Page not found'), 404


if __name__ == '__main__':
    app.run(debug=True)
