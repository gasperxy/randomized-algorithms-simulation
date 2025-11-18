from flask import Flask


def create_app() -> Flask:
    """Application factory for Randomized Experiments Lab."""
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY="dev")

    from .presentation.routes import pages_bp

    app.register_blueprint(pages_bp)
    return app
