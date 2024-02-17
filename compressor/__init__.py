from flask import Flask, redirect, render_template, request, url_for
from hashlib import sha256
from pathlib import Path
from .persistence import url_store
from urllib.parse import urlparse


def normalise_url(url: str) -> str:
    parsed_url = urlparse(request.form["url"])
    if parsed_url.scheme not in {"http", "https"}:
        parsed_url = parsed_url._replace(scheme="https")

    url_str = parsed_url.geturl()
    return url_str


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

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")
    
    @app.route("/<token>", methods=["GET", "PUT", "POST", "DELETE"])
    def redirect_to_full_url(token):
        full_url = url_store().get(token)
        return redirect(full_url)

    @app.route("/", methods=["POST"])
    def compress():
        url_str = normalise_url(request.form["url"])
        compressed_token = sha256(url_str.encode()).hexdigest()[:6]

        url_store().store(compressed_token, url_str)

        compressed = url_for("redirect_to_full_url", token=compressed_token, _external=True)
        return render_template("response.html", url=compressed)

    db.init_app(app)
    return app
