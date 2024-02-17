from flask import Flask, redirect, render_template, request, url_for
from urllib.parse import urlparse

from hashlib import sha256

shortened_urls = {}

def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")
    
    @app.route("/<token>", methods=["GET", "PUT", "POST", "DELETE"])
    def redirect_to_full_url(token):
        return redirect(shortened_urls[token].geturl())

    @app.route("/", methods=["POST"])
    def compress():
        url = urlparse(request.form["url"])
        if url.scheme not in {"http", "https"}:
            url = url._replace(scheme="https")

        url_str = url.geturl()
        compressed_token = sha256(url_str.encode()).hexdigest()[:6]
        shortened_urls[compressed_token] = url

        compressed = url_for("redirect_to_full_url", token=compressed_token, _external=True)
        return render_template("response.html", url=compressed)

    return app
