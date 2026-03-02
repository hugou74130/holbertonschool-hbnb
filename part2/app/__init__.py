from flask import Flask

from app.api.v1 import api_bp


def create_app() -> Flask:
    """Create and configure the Flask application.

    The API blueprint already sets up a :class:`flask_restx.Api`
    with all of the necessary namespaces, so we simply register
    it on the app with the proper URL prefix.
    """
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    return app
