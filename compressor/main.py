from .persistence import url_store
from flask import (
    Blueprint,
    make_response,
    redirect,
    render_template,
    request,
    Response,
    url_for,
)
from urllib.parse import urlparse


def normalise_url(url: str) -> str:
    parsed_url = urlparse(request.form["url"])
    if parsed_url.scheme not in {"http", "https"}:
        parsed_url = parsed_url._replace(scheme="https")

    url_str = parsed_url.geturl()
    return url_str


bp = Blueprint('main', __name__)


@bp.route("/", methods=["GET"])
def home() -> Response:
    resp = make_response(render_template("index.html"))
    return resp


@bp.route("/<token>", methods=["GET", "PUT", "POST", "DELETE"])
def redirect_to_full_url(token) -> Response:
    full_url = url_store().get(token)
    resp = make_response(redirect(full_url))
    return resp


@bp.route("/", methods=["POST"])
def compress() -> Response:
    url_str = normalise_url(request.form["url"])
    token = url_store().store(url_str)

    compressed = url_for("main.redirect_to_full_url", token=token, _external=True)
    resp = make_response(render_template("response.html", url=compressed))
    return resp
