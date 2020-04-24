import face_recognition as fr
import numpy as np
import os
import cv2
import face_recognition
import tkinter as tk
from tkinter import *
import pandas as pd
import datetime
import time
from PIL import Image,ImageTk
import csv


#TOLERANCE = 0.5
MODEL = "hog"
def classify_face():


    def get_encoded_faces():
        encoded = {}

        for dirpath, dnames, fnames in os.walk("./faces"):
            for f in fnames:
                if f.endswith(".jpg") or f.endswith(".png"):
                    face = fr.load_image_file("faces/" + f)
                    encoding = fr.face_encodings(face)[0]
                    encoded[f.split(".")[0]] = encoding

        return encoded

    def unknown_image_encoded(img):
        face = fr.load_image_file("faces/" + img)
        encoding = fr.face_encodings(face)[0]

        return encoding

    cap = cv2.VideoCapture(0)
    while True:

        process_this_frame = True

        faces = get_encoded_faces()
        faces_encoded = list(faces.values())
        known_face_names = list(faces.keys())
        ret, img = cap.read()
        # img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        # img = img[:,:,::-1]
        if process_this_frame:
            face_locations = face_recognition.face_locations(img, model=MODEL)
            unknown_face_encodings = face_recognition.face_encodings(img, face_locations)

            face_names = []
            for face_encoding in unknown_face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(faces_encoded, face_encoding)
                name = "Unknown"

                # use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Draw a box around the face
            cv2.rectangle(img, (left - 20, top - 20), (right + 20, bottom + 20), (255, 0, 0), 2)

            # Draw a label with a name below the face
            cv2.rectangle(img, (left - 20, bottom - 15), (right + 20, bottom + 20), (255, 0, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 2)

        # Display the resulting image

            cv2.imshow('Video', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(face_names)
            break



    cap.release()
    cv2.destroyAllWindows()
classify_face()