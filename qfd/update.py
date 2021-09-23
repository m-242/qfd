#!/usr/bin/env python3
# This file contains everything related to updating and cleaning the 
# bird songs list.

import os, uuid

def update_songs_database(data, data_path):
    """ This function is bound to the USR1 signal. It checks for new
    songs, sanitizes, masters, classifies them, and writes the data.json file. """
    # TODO logging
    files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
    for file in files:
        specie = analyze_song(file)
        if specie in data: # Do we know about this bird ?
            extract_name = clean_and_write(file, data_path)
            data[specie]["extracts"].append(extract_name)
        else:
            os.remove(os.path.join(data_path, file))

    return data

def analyze_song(filename):
    """ Reads a file and returns it's canonical name """
    # this is where machine learning happens
    return "TODO"

def clean_and_write(file, data_dir):
    """ Takes a file, cleans it, generates a uuid for it, writes
    it in the data directory and returns the uuid """
    uid = uuid.uuid4()
    # TODO clean & master

    os.rename(file, os.path.join(data_dir, str(uid)))

    return uid

