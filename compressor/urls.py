from flask import Blueprint, render_template, request, url_for
from .persistence import url_store


bp = Blueprint(
    name="urls",
    import_name=__name__,
    url_prefix="/urls",
    template_folder="templates",
    static_folder="static"
)


@bp.route("/", methods=["GET"])
def list_of_urls():
    token_map = url_store().all()
    urls = [
        (url, url_for("main.redirect_to_full_url", token=token, _external=True))
        for token, url in token_map.items()
    ]
    return render_template("list.html", urls=urls)
