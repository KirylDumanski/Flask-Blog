from flask import request, flash, render_template

from app.main import bp


@bp.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if len(request.form['username']) > 3:
            flash('Message sent', category='success')
        else:
            flash('Sending error', category='error')
    return render_template('main/feedback.html', title="Feedback!")
