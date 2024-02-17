import pytest

from bs4 import BeautifulSoup, Tag
from compressor import db, create_app, shortened_urls
from dataclasses import dataclass
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


@dataclass
class CompressorApp:
    app: Flask
    client: FlaskClient

    def shorten(self, url: str) -> str:
        response = self.client.post("/", data={"url": url})
        assert response.status_code == 200

        page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
        short_url_anchor = page.find("a", id="short-url")
        assert isinstance(short_url_anchor, Tag)

        shorten_href = short_url_anchor.attrs["href"]
        assert shorten_href is not None
        return shorten_href

    def redirect(self, short_url: str) -> str:
        response = self.client.get(short_url)
        assert response.status_code == 302
        return response.headers["Location"]


@pytest.fixture
def compressor_app(app: Flask, client: FlaskClient) -> CompressorApp:
    return CompressorApp(app, client)


def test_shorten_and_redirect_to_url(compressor_app: CompressorApp) -> None:
    arbitrary_url = "https://www.google.com"
    short_url = compressor_app.shorten(arbitrary_url)
    assert arbitrary_url not in short_url
    assert compressor_app.redirect(short_url) == arbitrary_url


def test_url_shortening_is_persistent(compressor_app: CompressorApp) -> None:
    arbitrary_url = "https://www.google.com"
    short_url = compressor_app.shorten(arbitrary_url)

    global shortened_urls
    shortened_urls.clear()

    assert compressor_app.redirect(short_url) == arbitrary_url


def test_shorten_the_same_url_twice_is_idempotent(compressor_app: CompressorApp) -> None:
    arbitrary_url = "https://www.xy.com"
    short_url = compressor_app.shorten(arbitrary_url)
    assert short_url == compressor_app.shorten(arbitrary_url)
