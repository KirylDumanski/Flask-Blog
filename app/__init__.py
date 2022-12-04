from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'success'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize login manager
    login_manager.init_app(app)

    # Initialize Flask extensions here
    db.init_app(app)

    # Register context processors here
    from app.context_processors import inject_mainmenu
    app.context_processor(inject_mainmenu)

    # Register template filters here
    from app.template_filters import iso_time
    app.jinja_env.filters['iso_time'] = iso_time

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.post import bp as post_bp
    app.register_blueprint(post_bp, url_prefix='/post')

    from app.errors import bp as error_bp
    app.register_blueprint(error_bp)

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app


from app import models
