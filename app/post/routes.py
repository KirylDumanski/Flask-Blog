from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from slugify import slugify
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound, IntegrityError

from app import db
from app.models import Post
from app.post import bp


@bp.route("/list")
def posts_list():
    posts = Post.query.order_by(desc(Post.date)).all()
    return render_template('post/posts_list.html', title='Main page', posts=posts)


@bp.route("/<int:post_id>/<string:post_slug>")
@login_required
def post_detail(post_id, post_slug):
    try:
        post = Post.query.filter_by(id=post_id, slug=post_slug).one()
    except NoResultFound:
        return render_template('page404.html', title='Page not found'), 404

    return render_template('post/post_detail.html', post=post, title=post.title)


@bp.route("/<int:post_id>/delete/")
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post successfully deleted!', category='success')
        return redirect(url_for('post.posts_list'))
    except Exception as e:
        print(e)
        flash('An error occurred while deleting', category='error')
        return render_template(url_for('post.post_detail', post_id=post.id, post_slug=post.slug),
                               title='Add post')


@bp.route("/<int:post_id>/update/", methods=["GET", "POST"])
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        try:
            post.title = request.form['title']
            post.text = str(request.form['text'])
            post.slug = slugify(request.form['title'])
            db.session.commit()
            flash('Post updated', category='success')
            return redirect(url_for('post.post_detail', post_id=post.id, post_slug=post.slug))
        except IntegrityError:
            db.session.rollback()
            flash('Update post error: Enter a unique post title!', category='error')

    return render_template('post/post_update.html', title='Update post', post=post)


@bp.route("/add", methods=["GET", "POST"])
@login_required
def post_add():
    if request.method == 'POST':
        try:
            post = Post(title=request.form['title'],
                        text=request.form['text'],
                        slug=slugify(request.form['title']))
            db.session.add(post)
            db.session.flush()
            flash('Post added', category='success')

        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Adding post error', category='error')
        else:
            db.session.commit()
            return redirect(url_for('post.post_detail', post_id=post.id, post_slug=post.slug))

    return render_template('post/post_add.html', title='Add post')
