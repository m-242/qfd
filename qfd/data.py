#!/usr/bin/env python3

# This files contains everything the qfd server uses to generate questions.

import json, random


def read_data_from_json(path):
    """This reads json and returns it"""
    with open(path, "r") as f:
        return json.load(f)


def generate_question(data):
    """This generates and returns a question in proper expected json format"""
    species = list(data.keys())
    q_specie = random.choice(species)
    question = {
        "file": random.choice(data[q_specie]["extracts"]),
        "label": data[q_specie]["display_name"],
        "image": data[q_specie]["display_image"],
    }

    labels = ["a", "b", "c"]  # TODO configurable labels ?
    random.shuffle(labels)

    # let's generate at least one correct answer
    answers = [
        {
            "label": labels.pop(),  # We will need to replace that
            "file": random.choice(data[q_specie]["extracts"]),
        }
    ]

    correct_answers = [answers[0]["label"]]

    while labels:
        x = labels.pop()
        r_specie = random.choice(species)
        answers.append(
            {
                "label": x,
                "file": random.choice(data[r_specie]["extracts"]),
            }
        )

        if r_specie == q_specie:
            correct_answers.append(x)

    random.shuffle(answers)

    return {
        "question": question,
        "answers": answers,
        "correct_answers": correct_answers,
    }
