from . import db

from dataclasses import dataclass, field
from flask import g
from hashlib import sha256
from sqlite3 import Connection, IntegrityError

class InvalidToken(ValueError):
    def __init__(self, token: str):
        super().__init__(f"Invalid token {token}")


def token_for_url(url: str) -> str:
    return sha256(url.encode("utf-8")).hexdigest()[:6]


@dataclass
class UrlStore:
    db: Connection
    cache: dict[str, str] = field(default_factory=dict)

    def drop_cache(self) -> None:
        self.cache = {}
    
    def get(self, token: str) -> str:
        if token in self.cache:
            return self.cache[token]
        cursor = self.db.cursor()
        cursor.execute('SELECT url FROM tokens WHERE token = ?', (token,))
        result = cursor.fetchone()
        if result is None:
            raise InvalidToken(token=token)

        url = result[0]
        self.cache[token] = url
        return url
    
    def store(self, url: str) -> str:
        token = token_for_url(url)

        cursor = self.db.cursor()
        try:
            cursor.execute('INSERT INTO tokens (token, url) VALUES (?, ?)', (token, url))
            self.db.commit()
        except IntegrityError:
            pass

        self.cache[token] = url
        return token
    
    def all(self) -> dict[str, str]:
        cursor = self.db.cursor()
        cursor.execute('SELECT token, url FROM tokens')
        self.cache.update({
            token: url
            for token, url in cursor.fetchall()
        })
        return self.cache


def url_store() -> UrlStore:
    if "url_store" not in g:
        g.url_store = UrlStore(db.sqlite_connection())
    return g.url_store