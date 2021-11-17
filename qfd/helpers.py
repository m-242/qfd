#!/usr/bin/env python3

# This file holds diverse helper functions.

import random
import datetime
import uuid


def reduce_state_local_vote(state):
    """Removes parts of the state a player that hasn't voted yet should have access to.
    Basically returns the labels of question choices"""
    choices = [i["label"] for i in state["qcm"]["answers"]]
    return choices


def check_answer_result(player_id, answer, state):
    """This sanitises the answer coming directly from the user and returns if
    it is the right answer or not."""
    # TODO Sanitize
    return (answer is not None and
    answer in state["qcm"]["correct_answers"])


def check_cookie_validity(cookie, state):
    """This function gets passed an id, and the state, and returns True
    if the cookie exists, and has not expired"""
    return (cookie is not None and cookie in state["players"])


def generate_player_name():
    """Generates a random player name using two lists"""
    prenoms= [
            "Ira",
            "Phanuel",
            "Nazaire",
            "Syéna",
            "Hervieu",
            "Judaël",
            "Théodren",
            "Marcion",
            "Timothée",
            "Ano",
            "Meurice",
            "Nicky",
            "Edric",
            "Oriane",
            "Loryne",
            "Chloé",
            "Firdaws",
            "Planchat",
            "Macé",
            "Sylphide",
            "Violetta",
            "Pourçain",
            "Ghislain",
            "Yvanne",
            "Bert",
            "Harold",
            "Gisela",
            "Eutochie",
            "Clélia",
            "German",
            "Pâquerette",
            "Constantine",
            "Derek",
            "Euphrosine",
            "Casilde",
            "Elfie",
            "Nadiège",
            "Katia",
            "Sibert",
            "Nicolle",
            "Matéli",
            "Guadalupe",
            "Abigaël",
            "Firmiane",
            "Bertranet",
            "Clarence",
            "Babylas",
            "Josse",
            "Zéra",
            "Dewi"
    ]
    noms = [
            "Pierre",
            "Lecours",
            "Lavoie",
            "Aubé",
            "Nadon",
            "Gouin",
            "Bisaillon",
            "St-Louis",
            "Beaumier",
            "Lemelin",
            "Tessier",
            "Lamontagne",
            "Labrecque",
            "Levasseur",
            "Beauchamp",
            "Angers",
            "Charest",
            "Corbeil",
            "Jacob",
            "Rose",
            "Pinette",
            "Wong",
            "Samson",
            "Cardin",
            "Jones",
            "Gilbert",
            "Hardy",
            "Marquis",
            "Valcourt",
            "Hamilton",
            "Rémillard",
            "Breton",
            "Constantineau",
            "Coutu",
            "Dagenais",
            "Ouimet",
            "Germain",
            "Brisson",
            "Audy",
            "Galarneau",
            "Taylor",
            "Talbot",
            "Savage",
            "Doré",
            "Mailhot",
            "Forgues",
            "Ringuette",
            "Lavigne",
            "Reid",
            "Rancourt"]
    return f"{random.choice(prenoms)} {random.choice(noms)}"
