#!/usr/bin/env python3
from flask import Flask, redirect, url_for, request, make_response, render_template
import uuid, datetime, threading, time, signal, os


from helpers import (
    check_answer_result,
    generate_player_name,
    check_cookie_validity,
    reduce_state_local_vote,
)
from data import read_data_from_json, generate_question
from update import update_songs_database, load_model

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
        app.config["STATE"]["players"]["last_active"] = datetime.datetime.now()
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
        "last_active": datetime.datetime(1970, 1, 1),
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
    player_id = request.cookies.get("id")
    if player_id is None:
        app.logger.info(
            f"{request.remote_addr} hit /local_vote without having a cookie"
        )
        return "Please auth", 403
    
    # TODO check if already answered
    win = check_answer_result(player_id, request.args.get("choice"), app.config["STATE"]) 
    if win:
        app.config["STATE"]["player"][player_id]["score"] += 10

    app.config["STATE"]["player"][player_id]["last_active"] = datetime.datetime.now()

    try:
        return render_template(
            "local_vote_result.html",
            state=app.config["STATE"],
            res=win,
        )
    except:
        # TODO proper answer
        app.logger.warn(
            "Got an error at local vote:\n\nrequest:{}".format(request)
        )
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


@app.before_first_request
def question_updating_thread():
    app.config["DATA"] = read_data_from_json(app.config["DATA_DIR"] + "/data.json")
    app.logger.info(os.getpid())

    def update_question():
        while True:
            app.config["STATE"]["qcm"] = generate_question(app.config["DATA"])
            app.logger.info("New question: {}".format(app.config["STATE"]["qcm"]))
            time.sleep(300)

    thread = threading.Thread(target=update_question)
    thread.start()


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
#     "correct_answers": ["...", "..."]
#     "generation_time": datetime object,
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

def signal_update_handler(s, f):
    app.logger.info("Got signal, analyzing new files...")
    app.config["DATA"] = update_songs_database(
            app.config["DATA"],
            app.config["DATA_DIR"] + "/new/",
            app.config["MODEL"])


if __name__ == "__main__":
    print("q")
    signal.signal(signal.SIGUSR1, signal_update_handler)

    # TODO proper config
    app.config["DATA_DIR"] = "./static/data/"
    app.config["MODEL"] = load_model("./static/model/")

    # FIXME using config to hold state isn't great, but I don't have a better
    # idea
    app.config["STATE"] = {"qcm": {}, "players": {}}

    # TODO this is a mock
    app.config["STATE"]["qcm"]["answers"] = [
        {"label": "a", "file": "..."},
        {"label": "b", "file": "..."},
    ]
    app.config["STATE"]["qcm"]["correct_answers"] = ["a"]

    question_updating_thread()
    app.run(debug=True, host="0.0.0.0")
