from flask import flash, redirect, url_for, render_template, request
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.auth import bp
from app.auth.forms import RegisterForm, LoginForm
from app.models import User, Profile


@bp.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            password_hash = generate_password_hash(form.password1.data)
            user = User(email=form.email.data,
                        password=password_hash)
            db.session.add(user)
            db.session.flush()

            user_profile = Profile(name=form.name.data,
                                   age=form.age.data,
                                   city=form.city.data,
                                   user_id=user.id)
            db.session.add(user_profile)
            db.session.commit()
            flash("You have successfully registered!", category='success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Registration error", category='error')

    return render_template('auth/register.html', title='Sign up', form=form)


@bp.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile'))

    form = LoginForm()
    if form.validate_on_submit():  # check if request.method == "POST", also use validators to check entered value
        try:
            user = User.query.filter_by(email=form.email.data).one()
            if user and check_password_hash(user.password, form.password.data):
                rm = form.remember.data
                login_user(user, remember=rm)
                return redirect(request.args.get('next') or url_for('auth.profile'))
            else:
                flash('Incorrect username and/or password entered', category='error')
        except NoResultFound:
            flash('Incorrect username and/or password entered', category='error')

    return render_template('auth/login.html', title='Authorization', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash('Logged out successfully', category='success')
    return redirect(url_for('post.posts_list'))


@bp.route("/profile")
@login_required
def profile():
    user = current_user
    return render_template('auth/profile.html', user=user)
