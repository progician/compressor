import click

from flask import current_app, g
from pathlib import Path
from sqlite3 import connect, Connection, PARSE_DECLTYPES, Row


def sqlite_connection() -> Connection:
    if "db" not in g:
        parent = Path(current_app.config["DATABASE"]).parent
        parent.mkdir(parents=True, exist_ok=True)
        g.db = connect(
            current_app.config["DATABASE"],
            detect_types=PARSE_DECLTYPES
        )
        g.db.row_factory = Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = sqlite_connection()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
