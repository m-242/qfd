#!/usr/bin/env python3

# This files contains everything the qfd server uses to generate questions.

import json, random


def read_data_from_json(path):
    """This reads json and returns it"""
    with open(path, "r") as f:
        return json.load(f)


def generate_question(data):
    """This generates and returns a question in proper expected json format"""
    # TODO
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
    return {}
