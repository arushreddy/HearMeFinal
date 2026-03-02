import tkinter as tk
import subprocess


# ---------- WINDOW ----------

root = tk.Tk()

root.title("HearMe Emergency")

root.geometry("1000x700")

root.configure(bg="#0f172a")


# ---------- TITLE BAR ----------

title_frame = tk.Frame(root,bg="#020617",height=70)

title_frame.pack(fill="x")


title = tk.Label(
title_frame,
text="🚨 HearMe Emergency Mode",
font=("Segoe UI",26,"bold"),
fg="#ef4444",
bg="#020617")

title.pack(pady=10)



subtitle = tk.Label(
title_frame,
text="Quick Communication for Urgent Situations",
font=("Segoe UI",12),
fg="white",
bg="#020617")

subtitle.pack()



# ---------- MESSAGE DISPLAY ----------

message_frame = tk.Frame(root,bg="#111827",
width=700,
height=150)

message_frame.pack(pady=40)

message_frame.pack_propagate(False)


message_box = tk.Label(
message_frame,
text="Select a Message",
font=("Segoe UI",32,"bold"),
fg="yellow",
bg="#111827",
wraplength=600)

message_box.pack(expand=True)



# ---------- SPEECH ----------

def speak(text):

    subprocess.Popen(
    ["python","speak.py",text]
    )



# ---------- FUNCTIONS ----------

def help_msg():

    text="Emergency please help me"

    message_box.config(
    text="🚨 PLEASE HELP ME 🚨")

    speak(text)



def doctor_msg():

    text="I need a doctor"

    message_box.config(
    text="I NEED A DOCTOR")

    speak(text)



def police_msg():

    text="Call the police"

    message_box.config(
    text="CALL POLICE")

    speak(text)



def water_msg():

    text="I need water"

    message_box.config(
    text="I NEED WATER")

    speak(text)



def restroom_msg():

    text="I need to use the restroom"

    message_box.config(
    text="🚻 I NEED RESTROOM")

    speak(text)



# ---------- BUTTON AREA ----------

btn_frame = tk.Frame(root,bg="#0f172a")

btn_frame.pack(pady=20)


btn_style={

"font":("Segoe UI",16,"bold"),

"width":18,

"height":2

}


tk.Button(
btn_frame,
text="🚨 HELP",
bg="#dc2626",
fg="white",
command=help_msg,
**btn_style).grid(row=0,column=0,padx=20,pady=20)



tk.Button(
btn_frame,
text="👨‍⚕️ DOCTOR",
bg="#ea580c",
fg="white",
command=doctor_msg,
**btn_style).grid(row=0,column=1,padx=20,pady=20)



tk.Button(
btn_frame,
text="🚔 POLICE",
bg="#2563eb",
fg="white",
command=police_msg,
**btn_style).grid(row=1,column=0,padx=20,pady=20)



tk.Button(
btn_frame,
text="💧 WATER",
bg="#16a34a",
fg="white",
command=water_msg,
**btn_style).grid(row=1,column=1,padx=20,pady=20)



tk.Button(
btn_frame,
text="🚻 RESTROOM",
bg="#7c3aed",
fg="white",
command=restroom_msg,
**btn_style).grid(row=2,column=0,padx=20,pady=20)



# ---------- BACK BUTTON ----------

tk.Button(
root,
text="Back",
font=("Segoe UI",14),
width=10,
command=root.destroy).pack(pady=40)



root.mainloop()