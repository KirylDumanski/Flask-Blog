from flask import render_template

from app.errors import bp


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Page not found'), 404
