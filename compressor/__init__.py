from flask import Flask, redirect, render_template, request, url_for
from pathlib import Path
from urllib.parse import urlparse

from hashlib import sha256

shortened_urls = {}

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
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    from . import db

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")
    
    @app.route("/<token>", methods=["GET", "PUT", "POST", "DELETE"])
    def redirect_to_full_url(token):
        conn = db.sqlite_connection()
        if token not in shortened_urls:
            res = conn.execute("SELECT token, url FROM tokens WHERE token = ?", (token,))
            row = res.fetchone()
            if row is None:
                return f"Invalid token {token}", 404
            shortened_urls[token] = urlparse(row["url"])

        return redirect(shortened_urls[token].geturl())

    @app.route("/", methods=["POST"])
    def compress():
        url = urlparse(request.form["url"])
        if url.scheme not in {"http", "https"}:
            url = url._replace(scheme="https")

        url_str = url.geturl()
        compressed_token = sha256(url_str.encode()).hexdigest()[:6]
        shortened_urls[compressed_token] = url
        conn = db.sqlite_connection()
        conn.execute("INSERT INTO tokens (token, url) VALUES (?, ?)", (compressed_token, url_str))
        conn.commit()

        compressed = url_for("redirect_to_full_url", token=compressed_token, _external=True)
        return render_template("response.html", url=compressed)

    db.init_app(app)
    return app
