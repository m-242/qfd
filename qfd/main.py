#!/usr/bin/env python3
from flask import Flask, redirect, url_for, request, make_response, render_template
import uuid
import datetime
from helpers import (
    check_answer_result,
    generate_player_name,
    check_cookie_validity,
    reduce_state_local_vote,
)

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


@app.route("/")
def index():
    """This is the main page. It checks if a user already has a name, gives them one
    if needed, and redirects to either local_vote or distant_vote"""
    id_cookie = request.cookies.get("id")
    # The user exists
    # Gotta play everyday to keep the cookie
    if check_cookie_validity(id_cookie, app.config["STATE"]):
        app.config["STATE"]["players"]["last_active"] = datetime.now()
        if app.config["STATE"]["players"]["is_local"]:
            app.logger.debug(f"local player {uuid.UUID(id_cookie)} joined back")
            return redirect(url_for("local_vote"))
        else:
            app.logger.debug(f"distant player {id_cookie} joined back")
            return redirect(url_for("distant_vote"))

    # The user is entirely new/has an expired cookie
    player_id = str(uuid.uuid4())
    player = {
        "name": generate_player_name(),
        "score": 0,
        "last_active": datetime.datetime.now(),
        "is_local": True,
    }
    app.config["STATE"]["players"][player_id] = player

    app.logger.info("Created player {}, named {}".format(player_id, player["name"]))

    resp = make_response(redirect(url_for("local_vote")))
    resp.set_cookie("id", str(player_id))

    return resp


@app.route("/local/vote")
def local_vote():
    """Displays the page where local players vote."""
    if request.cookies.get("id") is None:
        app.logger.info(
            f"{request.remote_addr} hit /local_vote without having a cookie"
        )
        # TODO this is probably worth monitoring
        return "Please auth", 403

    # TODO definition in case alternative frontend
    return render_template(
        "local_vote.html", state=reduce_state_local_vote(app.config["STATE"])
    )


@app.route("/local/vote_result")
def local_vote_result():
    """Displays the page that appears once local players have voted"""
    if request.cookies.get("id") is None:
        app.logger.info(
            f"{request.remote_addr} hit /local_vote without having a cookie"
        )
        # TODO this is probably worth monitoring
        return "Please auth", 403

    try:
        return render_template(
            "local_vote_result.html",
            state=app.config["STATE"],
            res=check_answer_result(app.config["STATE"], request.args["choice"]),
        )
    except:
        # TODO proper answer and logging
        return "brokennnnn", 404


@app.route("/distant/vote")
def distant_vote():
    # TODO auth
    return "", 200


@app.route("/distant/vote_result")
def distant_vote_result():
    return "", 200


@app.route("/state")
def state():
    """This function sends back the current state, it's polled by frontend
    to update the pages."""
    if request.cookies.get("id") is None:
        app.logger.info(
            f"{request.remote_addr} hit /local_vote without having a cookie"
        )
        # TODO this is probably worth monitoring
        return "Please auth", 403

    return app.config["STATE"]


# State contains the current question, and a player list, like so:
#
# {
#   "qcm": {
#     "question": {
#       "file": "...",
#       "label": "...",
#       "image": "..."
#     },
#     "answers": [
#       {
#         "label": "...",
#         "file": "..."
#       },
#       {
#         "label": "...",
#         "file": "..."
#       }
#     ],
#     "correct_answer": "..."
#   },
#   "players": {
#     "UUID": {
#       "name": "name",
#       "score": 0,
#       "last_active": "datetime object",
#       "is_local": "boolean"
#     }
#   }
# }


if __name__ == "__main__":
    # TODO Init

    # FIXME using config to hold state isn't great, but I don't have a better
    # idea
    app.config["STATE"] = {"qcm": {}, "players": {}}

    # TODO this is a mock
    app.config["STATE"]["qcm"]["answers"] = [
        {"label": "a", "file": "..."},
        {"label": "b", "file": "..."},
    ]
    app.config["STATE"]["qcm"]["correct_answer"] = "a"

    app.run(debug=True, host="0.0.0.0")
