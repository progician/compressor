import pytest

from bs4 import BeautifulSoup, Tag
from compressor import db, create_app, url_store
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

    def list_of_urls(self) -> dict[str, str]:
        response = self.client.get("/urls/")
        assert response.status_code == 200

        page = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
        list_items = page.find_all("li", class_="url-item")
        result = {
            item.find("a", class_="original-url").attrs["href"] : item.find("a", class_="short-url").attrs["href"]
            for item in list_items
        }
        return result


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

    with compressor_app.app.app_context():
        url_store().drop_cache()

    assert compressor_app.redirect(short_url) == arbitrary_url


def test_shorten_the_same_url_twice_is_idempotent(compressor_app: CompressorApp) -> None:
    arbitrary_url = "https://www.xy.com"
    short_url = compressor_app.shorten(arbitrary_url)
    assert short_url == compressor_app.shorten(arbitrary_url)


def test_listing_of_existing_urls(compressor_app: CompressorApp) -> None:
    list_of_urls_to_shorten = [
        "https://www.google.com",
        "https://www.facebook.com",
        "https://www.twitter.com",
    ]
    shortened_urls = {
        url: compressor_app.shorten(url)
        for url in list_of_urls_to_shorten
    }

    assert compressor_app.list_of_urls() == shortened_urls
