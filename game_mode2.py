import tkinter as tk
import cv2
import mediapipe as mp
import pickle
import numpy as np
import random
from PIL import Image, ImageTk
import os

# Load model
model = pickle.load(open("asl_model.pkl","rb"))

# MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

target_letter = random.choice(letters)

score = 0


# ---------- WINDOW ----------

root = tk.Tk()

root.title("HearMe Game Mode")

root.geometry("1000x650")

root.configure(bg="#121212")


# ---------- TITLE ----------

title = tk.Label(
root,
text="ASL Learning Game",
font=("Arial",28,"bold"),
fg="cyan",
bg="#121212")

title.pack(pady=10)


# ---------- TARGET LETTER ----------

target_label = tk.Label(
root,
text="Show Sign: "+target_letter,
font=("Arial",40),
fg="yellow",
bg="#121212")

target_label.pack()


# ---------- SCORE ----------

score_label = tk.Label(
root,
text="Score: 0",
font=("Arial",20),
fg="white",
bg="#121212")

score_label.pack(pady=10)


# ---------- RESULT ----------

result_label = tk.Label(
root,
text="Make the sign",
font=("Arial",20),
fg="white",
bg="#121212")

result_label.pack(pady=10)


# ---------- MAIN AREA ----------

main_frame = tk.Frame(root,bg="#121212")
main_frame.pack(pady=10)


video_label=tk.Label(main_frame)
video_label.grid(row=0,column=0,padx=20)


image_label=tk.Label(main_frame,bg="#121212")
image_label.grid(row=0,column=1,padx=20)


# ---------- LOAD IMAGE ----------

def load_image():

    path="asl_signs/"+target_letter+".png"

    if os.path.exists(path):

        img=Image.open(path)

        img=img.resize((250,250))

        photo=ImageTk.PhotoImage(img)

        image_label.config(image=photo)

        image_label.image=photo


load_image()


# ---------- NEXT LETTER ----------

def next_letter():

    global target_letter

    target_letter=random.choice(letters)

    target_label.config(
    text="Show Sign: "+target_letter)

    load_image()


tk.Button(root,
text="Next Letter",
font=("Arial",16),
command=next_letter).pack(pady=10)


tk.Button(root,
text="Back",
font=("Arial",14),
command=root.destroy).pack()


# ---------- CAMERA ----------

def update():

    global score,target_letter

    ret,frame=cap.read()

    frame=cv2.flip(frame,1)

    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    result=hands.process(rgb)

    detected="-"

    if result.multi_hand_landmarks:

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


        if detected==target_letter:

            result_label.config(
            text="Correct!",
            fg="lime")

            score+=1

            score_label.config(
            text="Score: "+str(score))

            next_letter()

        else:

            result_label.config(
            text="Detected: "+detected,
            fg="red")


    img=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    img=Image.fromarray(img)

    imgtk=ImageTk.PhotoImage(img)

    video_label.imgtk=imgtk

    video_label.configure(image=imgtk)

    video_label.after(10,update)


update()

root.mainloop()