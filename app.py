import tkinter as tk
import subprocess

root=tk.Tk()

root.title("HearMe")

root.geometry("800x600")

root.configure(bg="#121212")


# ---------- TITLE ----------

title=tk.Label(root,
text="HearMe",
font=("Arial",40,"bold"),
fg="cyan",
bg="#121212")

title.pack(pady=20)


subtitle=tk.Label(root,
text="Smart Communication Assistant",
font=("Arial",16),
fg="white",
bg="#121212")

subtitle.pack(pady=5)


# ---------- FUNCTIONS ----------

def translator():

    subprocess.Popen(
    ["python","translator_module.py"]
    )


def emergency():

    subprocess.Popen(
    ["python","emergency_mode.py"]
    )


def game():
    subprocess.Popen(
    ["python","game_mode2.py"]
    )


def speech():
    subprocess.Popen(
    ["python","two_way_mode.py"]
    )


# ---------- BUTTON STYLE ----------

btn_style={
"font":("Arial",16),
"width":20,
"height":2
}


# ---------- BUTTONS ----------

tk.Button(root,
text="Translator Mode",
command=translator,
**btn_style).pack(pady=15)


tk.Button(root,
text="Game Mode",
command=game,
**btn_style).pack(pady=15)


tk.Button(root,
text="Emergency Mode",
command=emergency,
**btn_style).pack(pady=15)


tk.Button(root,
text="Two Way Mode",
command=speech,
**btn_style).pack(pady=15)


tk.Button(root,
text="Exit",
bg="red",
fg="white",
font=("Arial",14),
command=root.destroy).pack(pady=20)


root.mainloop()