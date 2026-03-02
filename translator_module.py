import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
import pickle
import numpy as np
import time
import subprocess

# Load Model
model = pickle.load(open("asl_model.pkl","rb"))

# MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
max_num_hands=2,
min_detection_confidence=0.8)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)


# ---------- WINDOW ----------

root = tk.Tk()
root.title("HearMe Translator")

root.geometry("900x800")
root.configure(bg="#121212")


title=tk.Label(root,
text="HearMe Translator",
font=("Arial",28,"bold"),
fg="cyan",
bg="#121212")

title.pack(pady=10)


video_label=tk.Label(root)
video_label.pack()


status_label=tk.Label(root,
text="Status: No Hand",
font=("Arial",14),
fg="red",
bg="#121212")

status_label.pack(pady=5)


letter_label=tk.Label(root,
text="Letter: -",
font=("Arial",40,"bold"),
fg="yellow",
bg="#121212")

letter_label.pack(pady=10)


sentence_box=tk.Label(root,
text="Sentence:",
font=("Arial",25),
fg="lime",
bg="#121212",
wraplength=800)

sentence_box.pack(pady=20)


sentence=""
current_letter=""
start_time=time.time()


# ---------- SPEAK ----------

def speak_sentence():

    global sentence

    if sentence.strip()=="":
        return

    subprocess.Popen(
    ["python","speak.py",sentence])

    clear_sentence()



def clear_sentence():

    global sentence

    sentence=""

    sentence_box.config(text="Sentence:")



# ---------- BUTTONS ----------

btn_frame=tk.Frame(root,bg="#121212")
btn_frame.pack()


tk.Button(btn_frame,
text="Speak",
font=("Arial",16),
bg="green",
fg="white",
command=speak_sentence
).pack(side="left",padx=10)


tk.Button(btn_frame,
text="Clear",
font=("Arial",16),
bg="red",
fg="white",
command=clear_sentence
).pack(side="left",padx=10)


def close():

    cap.release()
    root.destroy()


tk.Button(root,
text="Back",
font=("Arial",14),
command=close
).pack(pady=10)


# ---------- CAMERA ----------

def update():

    global sentence,current_letter,start_time

    ret,frame=cap.read()

    frame=cv2.flip(frame,1)

    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    result=hands.process(rgb)

    detected="-"

    if result.multi_hand_landmarks:

        status_label.config(
        text="Status: Hand Detected",
        fg="lime")

        for hand in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS)

            data=[]

            for lm in hand.landmark:

                data.append(lm.x)
                data.append(lm.y)
                data.append(lm.z)

            data=np.array(data).reshape(1,-1)

            detected=model.predict(data)[0]


        letter_label.config(
        text="Letter: "+detected)


        if detected==current_letter:

            if time.time()-start_time>3:

                sentence+=detected+" "

                sentence_box.config(
                text="Sentence: "+sentence)

                start_time=time.time()

        else:

            current_letter=detected
            start_time=time.time()

    else:

        status_label.config(
        text="Status: No Hand",
        fg="red")

        letter_label.config(
        text="Letter: -")


    img=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    img=Image.fromarray(img)

    imgtk=ImageTk.PhotoImage(img)

    video_label.imgtk=imgtk

    video_label.configure(image=imgtk)

    video_label.after(10,update)


update()

root.mainloop()