from datetime import datetime

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from forms import LoginForm, RegisterForm

SECRET_KEY = 'development_key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///flask-site.db'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'success'

menu = [{"name": "Main page", "url": "index"},
        {"name": "Add post", "url": "add-post"},
        {"name": "Feedback", "url": "feedback"}
        ]


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


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500), nullable=True)
    date = db.Column(db.Integer, default=datetime.utcnow)
    profile = db.relationship('Profiles', backref='users', uselist=False)

    def __repr__(self):
        return f"<users {self.id}>"

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer)
    city = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"profiles {self.id}"


@app.route("/index")
@app.route("/")
def index():
    articles = Article.query.order_by(desc(Article.date)).all()
    return render_template('index.html', title='Main page', articles=articles)


@app.route("/post/<int:post_id>/<string:post_slug>")
@login_required
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
@login_required
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


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            password_hash = generate_password_hash(form.password1.data)
            user = Users(email=form.email.data,
                         password=password_hash)
            db.session.add(user)
            db.session.flush()

            user_profile = Profiles(name=form.name.data,
                                    age=form.age.data,
                                    city=form.city.data,
                                    user_id=user.id)
            db.session.add(user_profile)
            db.session.commit()
            flash("You have successfully registered!", category='success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Registration error", category='error')

    return render_template('register.html', title='Sign up', form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():  # check if request.method == "POST", also use validators to check entered value
        try:
            user = Users.query.filter_by(email=form.email.data).one()
            if user and check_password_hash(user.password, form.password.data):
                rm = form.remember.data
                login_user(user, remember=rm)
                flash('Logged in successfully.', category='success')
                return redirect(request.args.get('next') or url_for('profile'))
            else:
                flash('Incorrect username and/or password entered', category='error')
        except NoResultFound:
            flash('Incorrect username and/or password entered', category='error')

    return render_template('login.html', title='Authorization', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash('Logged out successfully', category='success')
    return redirect(url_for('index'))


@app.route("/profile")
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Page not found'), 404


if __name__ == '__main__':
    app.run(debug=True)
