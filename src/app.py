from flask import Flask
from src.views import blueprints
from flask_cors import CORS
from src.utility.db import db_init

__all__ = ('create_app',)

def create_app(config=None, app_name='image-storage'):
    '''
    Initializes the application and its utilities.
    '''

    app = Flask(app_name)
    CORS(app)

    if config:
        app.config.from_pyfile(config)

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db_init()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5005)
