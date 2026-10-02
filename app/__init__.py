from flask import Flask

from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    from .routes.main import main_bp
    from .routes.exam import exam_bp
    from .routes.result import result_bp
    from .routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
