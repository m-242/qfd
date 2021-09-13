#!/usr/bin/env python3
from flask import Flask


## Setting up a proper Flask logging
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


app = Flask(__name__)


# Imports des routes TODO
@app.route("/")
def index():
    app.logger.info("got a hit on index")
    return ""


@app.route("/local_connect")
def local_connect():
    player = request.cookies.get("id")
    return ""


if __name__ == "__main__":
    # TODO Init

    # TODO using config to hold state isn't great, but I don't have a better
    # idea
    app.config["STATE"] = {"question": {}, "players": []}

    app.run(debug=True, host="0.0.0.0")
