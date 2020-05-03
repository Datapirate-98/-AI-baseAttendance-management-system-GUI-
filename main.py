import sys
from email.mime.multipart import MIMEMultipart

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
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



TOLERANCE = 0.5
MODEL = "hog"


import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import main_support
import os.path

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    global prog_location
    prog_call = sys.argv[0]
    prog_location = os.path.split(prog_call)[0]
    root = tk.Tk()
    top = Toplevel1 (root)
    main_support.init(root, top)
    root.mainloop()

w = None
def create_Toplevel1(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_Toplevel1(root, *args, **kwargs)' .'''
    global w, w_win, root
    global prog_location
    prog_call = sys.argv[0]
    prog_location = os.path.split(prog_call)[0]
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    top = Toplevel1 (w)
    main_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Toplevel1():
    global w
    w.destroy()
    w = None

class Toplevel1:


    def clear_func1(self):
        length_1 = len(self.subject_entry.get())
        self.subject_entry.delete(length_1 - 1, "end")
    def clear_func2(self):
        length_2 = len(self.room_entry.get())
        self.room_entry.delete(length_2-1, "end")
    def clear_func3(self):
        length_3 = len(self.email_entry.get())
        self.email_entry.delete(length_3-1, "end")
    def clear_func4(self):
        length_4 = len(self.filename_entry.get())
        self.filename_entry.delete(length_4-1, "end")




    def classify_face(self):

        subject = self.subject_entry.get()
        room = self.room_entry.get()

        if subject == "" or room == "":
            messagebox.showinfo("Error", "Invalid Subject or Room")
        else:
            subject_list = list(subject.split(" "))
            room_list = list(room.split(" "))
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
            cap.set(cv2.CAP_PROP_FPS, 60)
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
                        face_distances = face_recognition.face_distance(faces_encoded,face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

                process_this_frame = not process_this_frame

                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Draw a box around the face
                    cv2.rectangle(img, (left - 20, top - 20), (right + 20, bottom + 20), (255, 0,0), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(img, (left - 20, bottom - 15), (right + 20, bottom + 20), (255, 0, 0), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(img, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 2)

                # Display the resulting image

                    cv2.imshow('Video', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    #list_joint = face_names + subject + room
                    subjects = subject_list * len(face_names)
                    room = room_list * len(face_names)
                    dict = {"Name":face_names, "Subject":subjects, "Classroom":room}
                    df = pd.DataFrame(dict)
                    df.to_csv(subject + ".csv", index = False)
                    break



            cap.release()
            cv2.destroyAllWindows()

    def send_email(self):

        MailId = self.email_entry.get()
        file = self.filename_entry.get()

        if MailId == "" or file == "":
            messagebox.showinfo("Error", "Invalid Subject or Room")
        else:
            messagebox.showinfo("Done", "Mail Sent!")
        email_user = 'YOUR_MAILID'
        email_password = 'YOUR_MAILID_PASSWORD'
        email_send = MailId

        mail_subject = 'Attendance of your class'

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = mail_subject

        body = 'The attendance sheet is attached yn this mail'
        msg.attach(MIMEText(body, 'plain'))

        filename = file + ".csv"
        attachment = open(filename, 'rb')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= " + filename)

        msg.attach(part)
        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)

        server.sendmail(email_user, email_send, text)
        server.quit()




    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        font10 = "-family {Algerian} -size 24 -weight bold -underline "  \
            "1"
        font12 = "-family {Arial Black} -size 9 -weight bold"
        font15 = "-family {Arial} -size 14 -weight bold"

        top.geometry("901x700")
        top.minsize(148, 1)
        top.maxsize(1924, 1055)
        top.resizable(1, 1)
        top.title("ARCH")
        top.configure(borderwidth="5")
        top.configure(background="#000000")

        self.attending = tk.Frame(top)
        self.attending.place(relx=0.011, rely=0.186, relheight=0.807
                , relwidth=0.483)
        self.attending.configure(relief='groove')
        self.attending.configure(borderwidth="2")
        self.attending.configure(relief="groove")
        self.attending.configure(background="#000000")

        self.subject_entry = tk.Entry(self.attending)
        self.subject_entry.place(relx=0.253, rely=0.319, height=44
                , relwidth=0.722)
        self.subject_entry.configure(background="white")
        self.subject_entry.configure(disabledforeground="#a3a3a3")
        self.subject_entry.configure(font="TkFixedFont")
        self.subject_entry.configure(foreground="#000000")
        self.subject_entry.configure(insertbackground="black")

        self.room_entry = tk.Entry(self.attending)
        self.room_entry.place(relx=0.253, rely=0.566,height=44, relwidth=0.722)
        self.room_entry.configure(background="white")
        self.room_entry.configure(disabledforeground="#a3a3a3")
        self.room_entry.configure(font="TkFixedFont")
        self.room_entry.configure(foreground="#000000")
        self.room_entry.configure(insertbackground="black")

        self.subject_label = tk.Label(self.attending)
        self.subject_label.place(relx=0.023, rely=0.319, height=45, width=92)
        self.subject_label.configure(activebackground="#e1031e")
        self.subject_label.configure(activeforeground="white")
        self.subject_label.configure(background="#e1031e")
        self.subject_label.configure(borderwidth="10")
        self.subject_label.configure(disabledforeground="#a3a3a3")
        self.subject_label.configure(font=font12)
        self.subject_label.configure(foreground="#000000")
        self.subject_label.configure(text='''Subject''')

        self.room_label = tk.Label(self.attending)
        self.room_label.place(relx=0.023, rely=0.566, height=45, width=92)
        self.room_label.configure(background="#e1031e")
        self.room_label.configure(disabledforeground="#a3a3a3")
        self.room_label.configure(font=font12)
        self.room_label.configure(foreground="#000000")
        self.room_label.configure(text='''Room''')

        self.clear1 = tk.Button(self.attending)
        self.clear1.place(relx=0.483, rely=0.425, height=43, width=86)
        self.clear1.configure(activebackground="#ececec")
        self.clear1.configure(activeforeground="#000000")
        self.clear1.configure(background="#e1031e")
        self.clear1.configure(borderwidth="5")
        self.clear1.configure(disabledforeground="#a3a3a3")
        self.clear1.configure(font=font12)
        self.clear1.configure(foreground="#000000")
        self.clear1.configure(highlightbackground="#d9d9d9")
        self.clear1.configure(highlightcolor="black")
        self.clear1.configure(pady="0")
        self.clear1.configure(text='''Clear''')
        self.clear1.configure(command = self.clear_func1)

        self.clear2 = tk.Button(self.attending)
        self.clear2.place(relx=0.483, rely=0.673, height=43, width=86)
        self.clear2.configure(activebackground="#ececec")
        self.clear2.configure(activeforeground="#000000")
        self.clear2.configure(background="#e1031e")
        self.clear2.configure(borderwidth="5")
        self.clear2.configure(disabledforeground="#a3a3a3")
        self.clear2.configure(font=font12)
        self.clear2.configure(foreground="#000000")
        self.clear2.configure(highlightbackground="#d9d9d9")
        self.clear2.configure(highlightcolor="black")
        self.clear2.configure(pady="0")
        self.clear2.configure(text='''Clear''')
        self.clear2.configure(command = self.clear_func2)

        self.take_atten = tk.Button(self.attending)
        self.take_atten.place(relx=0.184, rely=0.832, height=73, width=276)
        self.take_atten.configure(activebackground="#ececec")
        self.take_atten.configure(activeforeground="#000000")
        self.take_atten.configure(background="#e1031e")
        self.take_atten.configure(borderwidth="5")
        self.take_atten.configure(disabledforeground="#a3a3a3")
        self.take_atten.configure(font=font15)
        self.take_atten.configure(foreground="#000000")
        self.take_atten.configure(highlightbackground="#d9d9d9")
        self.take_atten.configure(highlightcolor="black")
        self.take_atten.configure(pady="0")
        self.take_atten.configure(text='''Take Attendance''')
        self.take_atten.configure(command = self.classify_face)

        self.att_img = tk.Label(self.attending)
        self.att_img.place(relx=0.023, rely=0.008, height=166, width=414)
        self.att_img.configure(background="#d9d9d9")
        self.att_img.configure(disabledforeground="#a3a3a3")
        self.att_img.configure(foreground="#000000")
        photo_location = os.path.join(prog_location,"Attendance_Awareness_Blog__Generic_Header (1).png")
        global _img0
        _img0 = tk.PhotoImage(file=photo_location)
        self.att_img.configure(image=_img0)
        self.att_img.configure(text='''Label''')

        self.sending = tk.Frame(top)
        self.sending.place(relx=0.501, rely=0.186, relheight=0.806
                , relwidth=0.494)
        self.sending.configure(relief='groove')
        self.sending.configure(borderwidth="2")
        self.sending.configure(relief="groove")
        self.sending.configure(background="#000000")

        self.filename_entry = tk.Entry(self.sending)
        self.filename_entry.place(relx=0.225, rely=0.567, height=44
                , relwidth=0.751)
        self.filename_entry.configure(background="white")
        self.filename_entry.configure(disabledforeground="#a3a3a3")
        self.filename_entry.configure(font="TkFixedFont")
        self.filename_entry.configure(foreground="#000000")
        self.filename_entry.configure(insertbackground="black")

        self.email_entry = tk.Entry(self.sending)
        self.email_entry.place(relx=0.202, rely=0.319, height=44, relwidth=0.773)

        self.email_entry.configure(background="white")
        self.email_entry.configure(disabledforeground="#a3a3a3")
        self.email_entry.configure(font="TkFixedFont")
        self.email_entry.configure(foreground="#000000")
        self.email_entry.configure(insertbackground="black")

        self.email_label = tk.Label(self.sending)
        self.email_label.place(relx=0.022, rely=0.319, height=46, width=72)
        self.email_label.configure(background="#e1031e")
        self.email_label.configure(disabledforeground="#a3a3a3")
        self.email_label.configure(font=font12)
        self.email_label.configure(foreground="#000000")
        self.email_label.configure(text='''Email''')

        self.filename_label = tk.Label(self.sending)
        self.filename_label.place(relx=0.022, rely=0.567, height=46, width=82)
        self.filename_label.configure(background="#e1031e")
        self.filename_label.configure(disabledforeground="#a3a3a3")
        self.filename_label.configure(font=font12)
        self.filename_label.configure(foreground="#000000")
        self.filename_label.configure(text='''Filename''')

        self.clear3 = tk.Button(self.sending)
        self.clear3.place(relx=0.449, rely=0.426, height=44, width=86)
        self.clear3.configure(activebackground="#ececec")
        self.clear3.configure(activeforeground="#000000")
        self.clear3.configure(background="#e1031e")
        self.clear3.configure(borderwidth="5")
        self.clear3.configure(disabledforeground="#a3a3a3")
        self.clear3.configure(font=font12)
        self.clear3.configure(foreground="#000000")
        self.clear3.configure(highlightbackground="#d9d9d9")
        self.clear3.configure(highlightcolor="black")
        self.clear3.configure(pady="0")
        self.clear3.configure(text='''Clear''')
        self.clear3.configure(command = self.clear_func3)

        self.clear4 = tk.Button(self.sending)
        self.clear4.place(relx=0.449, rely=0.674, height=43, width=86)
        self.clear4.configure(activebackground="#ececec")
        self.clear4.configure(activeforeground="#000000")
        self.clear4.configure(background="#e1031e")
        self.clear4.configure(borderwidth="5")
        self.clear4.configure(disabledforeground="#a3a3a3")
        self.clear4.configure(font=font12)
        self.clear4.configure(foreground="#000000")
        self.clear4.configure(highlightbackground="#d9d9d9")
        self.clear4.configure(highlightcolor="black")
        self.clear4.configure(pady="0")
        self.clear4.configure(text='''Clear''')
        self.clear4.configure(command = self.clear_func4)

        self.mail_img = tk.Label(self.sending)
        self.mail_img.place(relx=0.022, rely=0.008, height=166, width=422)
        self.mail_img.configure(background="#d9d9d9")
        self.mail_img.configure(disabledforeground="#a3a3a3")
        self.mail_img.configure(foreground="#000000")
        photo_location = os.path.join(prog_location,"06VF4ZcETlFMvRHqRu6dDX0-1.fit_lim.v_1569492704(2).png")
        global _img1
        _img1 = tk.PhotoImage(file=photo_location)
        self.mail_img.configure(image=_img1)
        self.mail_img.configure(text='''Label''')

        self.submit_mail = tk.Button(self.sending)
        self.submit_mail.place(relx=0.202, rely=0.833, height=73, width=276)
        self.submit_mail.configure(activebackground="#ececec")
        self.submit_mail.configure(activeforeground="#000000")
        self.submit_mail.configure(background="#e1031e")
        self.submit_mail.configure(borderwidth="5")
        self.submit_mail.configure(disabledforeground="#a3a3a3")
        self.submit_mail.configure(font=font15)
        self.submit_mail.configure(foreground="#000000")
        self.submit_mail.configure(highlightbackground="#d9d9d9")
        self.submit_mail.configure(highlightcolor="black")
        self.submit_mail.configure(pady="0")
        self.submit_mail.configure(text='''Send''')
        self.submit_mail.configure(command = self.send_email)

        self.Frame3 = tk.Frame(top)
        self.Frame3.place(relx=0.0, rely=0.0, relheight=0.179, relwidth=0.994)
        self.Frame3.configure(relief='groove')
        self.Frame3.configure(borderwidth="5")
        self.Frame3.configure(relief="groove")
        self.Frame3.configure(background="#e1031e")

        self.Label1 = tk.Label(self.Frame3)
        self.Label1.place(relx=0.357, rely=0.24, height=66, width=251)
        self.Label1.configure(background="#d70428")
        self.Label1.configure(borderwidth="5")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(font=font10)
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(text='''A. R. C. H''')

if __name__ == '__main__':
    vp_start_gui()





