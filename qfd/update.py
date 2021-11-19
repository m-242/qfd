#!/usr/bin/env python3
# This file contains everything related to updating and cleaning the
# bird songs list.

import os, uuid, time

import numpy as np
import librosa
import operator

try:
    import tflite_runtime.interpreter as tflite
except:
    from tensorflow import lite as tflite


def update_songs_database(data, data_path, model):
    """This function is bound to the USR1 signal. It checks for new
    songs, sanitizes, masters, classifies them, and writes the data.json file."""
    # TODO logging
    print(data_path)
    files = [
        f
        for f in os.listdir(data_path + "/new/")
        if os.path.isfile(os.path.join(data_path + "/new/", f))
    ]
    print(f"analyzing files {files}")
    for file in files:
        print(file)
        specie = analyze_song(data_path + "/new/" + file, model)
        print(specie)
        if specie in data:  # Do we know about this bird ?
            extract_name = clean_and_write(file, data_path, model)
            data[specie]["extracts"].append(str(extract_name))
        else:
            os.remove(os.path.join(data_path + "/new/", file))

    # TODO unload model
    return data


def analyze_song(filename, model):
    """Reads a file and returns it's canonical name"""
    # this is where machine learning happens
    c = read_audio_data(filename, 0.0)
    zz = analyze_chunks(c, model)

    if zz[1] < 0.8:
        return "unknown"
    return zz[0]


def clean_and_write(file, data_dir, interpreter):
    """Takes a file, cleans it, generates a uuid for it, writes
    it in the data directory and returns the uuid"""
    uid = uuid.uuid4()
    # TODO clean & master

    os.rename(os.path.join(data_dir + "/new/", file), os.path.join(data_dir, str(uid)))

    return uid


def read_audio_data(path, overlap=0.0, sample_rate=48000):

    print("READING AUDIO DATA...", end=" ", flush=True)

    # Open file with librosa (uses ffmpeg or libav)
    sig, rate = librosa.load(path, sr=sample_rate, mono=True, res_type="kaiser_fast")

    # Split audio into 3-second chunks
    chunks = splitSignal(sig, rate, overlap)

    print("DONE! READ", str(len(chunks)), "CHUNKS.")

    return chunks


def analyze_chunks(
    chunks, interpreter, lat=-1, lon=-1, week=-1, sensitivity=1.0, overlap=0.0
):

    detections = {}
    start = time.time()
    print("ANALYZING AUDIO...", end=" ", flush=True)

    # Convert and prepare metadata
    mdata = convertMetadata(np.array([lat, lon, week]))
    mdata = np.expand_dims(mdata, 0)

    # Parse every chunk
    pred_start = 0.0
    for c in chunks:

        # Prepare as input signal
        sig = np.expand_dims(c, 0)

        # Make prediction
        p = predict([sig, mdata], interpreter, sensitivity)

        # Save result and timestamp
        pred_end = pred_start + 3.0
        detections[str(pred_start) + ";" + str(pred_end)] = p
        pred_start = pred_end - overlap

    print("DONE! Time", int((time.time() - start) * 10) / 10.0, "SECONDS")

    #  Get the highest detection
    max_y = ("eee", 0.0)
    for k in detections.keys():
        for z in detections[k]:
            if z[1] > max_y[1]:
                max_y = z

    return max_y


def load_model(base_path):
    """loads the model"""

    global INPUT_LAYER_INDEX
    global OUTPUT_LAYER_INDEX
    global MDATA_INPUT_INDEX
    global CLASSES

    print("LOADING TF LITE MODEL...", end=" ")

    # Load TFLite model and allocate tensors.
    interpreter = tflite.Interpreter(
        model_path=os.path.join(base_path, "BirdNET_6K_GLOBAL_MODEL.tflite")
    )
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Get input tensor index
    INPUT_LAYER_INDEX = input_details[0]["index"]
    MDATA_INPUT_INDEX = input_details[1]["index"]
    OUTPUT_LAYER_INDEX = output_details[0]["index"]

    # Load labels
    CLASSES = []
    with open(os.path.join(base_path, "labels.txt"), "r") as lfile:
        for line in lfile.readlines():
            CLASSES.append(line.replace("\n", ""))

    print("DONE!")

    return interpreter


def splitSignal(sig, rate, overlap, seconds=3.0, minlen=1.5):

    # Split signal with overlap
    sig_splits = []
    for i in range(0, len(sig), int((seconds - overlap) * rate)):
        split = sig[i : i + int(seconds * rate)]

        # End of signal?
        if len(split) < int(minlen * rate):
            break

        # Signal chunk too short? Fill with zeros.
        if len(split) < int(rate * seconds):
            temp = np.zeros((int(rate * seconds)))
            temp[: len(split)] = split
            split = temp

        sig_splits.append(split)

    return sig_splits


def convertMetadata(m):

    # Convert week to cosine
    if m[2] >= 1 and m[2] <= 48:
        m[2] = math.cos(math.radians(m[2] * 7.5)) + 1
    else:
        m[2] = -1

    # Add binary mask
    mask = np.ones((3,))
    if m[0] == -1 or m[1] == -1:
        mask = np.zeros((3,))
    if m[2] == -1:
        mask[2] = 0.0

    return np.concatenate([m, mask])


def custom_sigmoid(x, sensitivity=1.0):
    return 1 / (1.0 + np.exp(-sensitivity * x))


def predict(sample, interpreter, sensitivity):

    # Make a prediction
    interpreter.set_tensor(INPUT_LAYER_INDEX, np.array(sample[0], dtype="float32"))
    interpreter.set_tensor(MDATA_INPUT_INDEX, np.array(sample[1], dtype="float32"))
    interpreter.invoke()
    prediction = interpreter.get_tensor(OUTPUT_LAYER_INDEX)[0]

    # Apply custom sigmoid
    p_sigmoid = custom_sigmoid(prediction, sensitivity)

    # Get label and scores for pooled predictions
    p_labels = dict(zip(CLASSES, p_sigmoid))

    # Sort by score
    p_sorted = sorted(p_labels.items(), key=operator.itemgetter(1), reverse=True)

    # Remove species that are on blacklist
    for i in range(min(10, len(p_sorted))):
        if p_sorted[i][0] in ["Human_Human", "Non-bird_Non-bird", "Noise_Noise"]:
            p_sorted[i] = (p_sorted[i][0], 0.0)

    # Only return first the top ten results
    return p_sorted[:10]
