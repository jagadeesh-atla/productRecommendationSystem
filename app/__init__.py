from flask import Flask

from .views import *

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'flipkartGRID5-SOFTWARE'
    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app