from flask import Flask
from views import blueprints
from flask_cors import CORS
from db.db_utility import db_init
from tools.img_tools import *

__all__ = ('create_app',)

def create_app(config=None, app_name='image-storage'):
    '''
    Initializes the application and its utilities.
    '''
    global current_model
    app = Flask(app_name)
    CORS(app)

    if config:
        app.config.from_pyfile(config)

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    model_init()
    db_init()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5005)
