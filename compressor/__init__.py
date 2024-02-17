from flask import Flask, redirect, render_template, request, url_for
from hashlib import sha256
from pathlib import Path
from .persistence import url_store
from urllib.parse import urlparse


def create_app(test_config=None) -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )

    app.config.from_mapping(
        DATABASE=(Path(app.instance_path)/"compressor.db").as_posix(),
    )
    if test_config is None:
        app.config.from_prefixed_env(prefix="COMPRESSOR")
    else:
        app.config.from_mapping(test_config)

    from . import db

    from . import urls
    app.register_blueprint(urls.bp)

    from . import main
    app.register_blueprint(main.bp)

    db.init_app(app)
    return app
