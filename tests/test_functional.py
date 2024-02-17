import pytest

from compressor import db
from bs4 import BeautifulSoup
from compressor import create_app, shortened_urls
from flask import Flask
from flask.testing import FlaskClient
from pathlib import Path

@pytest.fixture
def app(tmp_path: Path) -> Flask:
    app = create_app()
    app.config.from_mapping(DATABASE = (tmp_path/"compressor.db").as_posix())

    with app.app_context():
        db.init_db()

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    app.testing = True
    client = app.test_client()
    return client


def test_shorten_and_redirect_to_url(client: FlaskClient):
    url = "https://www.google.com"
    response = client.post("/", data={"url": url})
    assert response.status_code == 200

    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    short_url_anchor = page.find("a", id="short-url")
    assert short_url_anchor is not None

    short_url = short_url_anchor.attrs["href"]

    assert short_url is not None and short_url != url and url not in short_url

    response = client.get(short_url)
    assert response.status_code == 302
    assert response.headers["Location"] == url


def test_url_shortening_is_persistent(client: FlaskClient):
    url = "https://www.google.com"
    response = client.post("/", data={"url": url})
    assert response.status_code == 200

    global shortened_urls
    shortened_urls.clear()

    page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    short_url_anchor = page.find("a", id="short-url")
    assert short_url_anchor is not None

    short_url = short_url_anchor.attrs["href"]

    assert short_url is not None and short_url != url and url not in short_url

    response = client.get(short_url)
    assert response.status_code == 302
    assert response.headers["Location"] == url
