import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import pickle
import numpy as np
import time
import subprocess
import os
import sys
import threading
import speech_recognition as sr
import pyttsx3

# ── Base dir & model ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    model = pickle.load(open(os.path.join(BASE_DIR, "asl_model.pkl"), "rb"))
    MODEL_LOADED = True
except:
    MODEL_LOADED = False
    print("⚠  asl_model.pkl not found – hand sign prediction disabled")

# ── MediaPipe ─────────────────────────────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

# ── Speech recognizer ─────────────────────────────────────────────────────────
recognizer = sr.Recognizer()

# ── TTS engine (thread-safe via subprocess) ───────────────────────────────────
TTS_RATE   = 150
TTS_VOLUME = 1.0

def speak_text(text):
    """Speak in a daemon thread so UI never freezes."""
    def _run():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', TTS_RATE)
            engine.setProperty('volume', TTS_VOLUME)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print("TTS error:", e)
    t = threading.Thread(target=_run, daemon=True)
    t.start()

# ═════════════════════════════════════════════════════════════════════════════
#  WINDOW
# ═════════════════════════════════════════════════════════════════════════════
root = tk.Tk()
root.title("Two-Way Communication Assistant")
root.configure(bg="#0d0d0d")
root.state("zoomed")

ACCENT_ASL   = "#f39c12"   # orange  – ASL side
ACCENT_VOICE = "#1e90ff"   # blue    – Voice side
BG           = "#0d0d0d"
CARD_BG      = "#1a1a2e"
DIVIDER      = "#2c2c54"

# ── Title bar ─────────────────────────────────────────────────────────────────
title_bar = tk.Frame(root, bg=DIVIDER)
title_bar.pack(fill="x")

tk.Label(title_bar,
         text="✋  TWO-WAY COMMUNICATION ASSISTANT  🎤",
         font=("Arial", 20, "bold"),
         fg="white", bg=DIVIDER).pack(pady=8)

# ── Main 3-column layout ──────────────────────────────────────────────────────
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=8, pady=6)

# ─────────────────────── LEFT  – ASL Person ───────────────────────────────────
left = tk.Frame(main, bg=CARD_BG, bd=2, relief="ridge")
left.pack(side="left", fill="both", expand=True, padx=(0, 4))

tk.Label(left, text="✋  SIGN PERSON  (ASL → Text)",
         font=("Arial", 14, "bold"), fg=ACCENT_ASL, bg=CARD_BG).pack(pady=6)

video_label = tk.Label(left, bg="black")
video_label.pack(padx=6)

asl_status = tk.Label(left, text="Hand: No Hand",
                       font=("Arial", 12), fg="red", bg=CARD_BG)
asl_status.pack(pady=2)

asl_letter = tk.Label(left, text="Letter: -",
                       font=("Arial", 36, "bold"), fg="yellow", bg=CARD_BG)
asl_letter.pack(pady=2)

# ASL sentence display
tk.Label(left, text="ASL Sentence:", font=("Arial", 12), fg="gray", bg=CARD_BG).pack(anchor="w", padx=10)
asl_sentence_var = tk.StringVar(value="")
asl_sentence_box = tk.Label(left, textvariable=asl_sentence_var,
                              font=("Arial", 16), fg="cyan", bg=CARD_BG,
                              wraplength=380, justify="left", anchor="w")
asl_sentence_box.pack(fill="x", padx=10, pady=4)

hold_progress = tk.Label(left, text="Hold: ░░░░░░░░░░  0%",
                          font=("Courier", 12), fg="#777", bg=CARD_BG)
hold_progress.pack(pady=2)

asl_btn_frame = tk.Frame(left, bg=CARD_BG)
asl_btn_frame.pack(pady=6)

# ─────────────────────── CENTER  – Shared chat log ────────────────────────────
center = tk.Frame(main, bg=DIVIDER, bd=2, relief="ridge", width=340)
center.pack(side="left", fill="both", padx=4)
center.pack_propagate(False)

tk.Label(center, text="💬  CONVERSATION",
         font=("Arial", 14, "bold"), fg="white", bg=DIVIDER).pack(pady=6)

chat_text = tk.Text(center, font=("Arial", 13), bg="#0a0a1a", fg="white",
                     state="disabled", wrap="word", relief="flat")
chat_text.pack(fill="both", expand=True, padx=6, pady=4)
chat_text.tag_config("asl",   foreground=ACCENT_ASL)
chat_text.tag_config("voice", foreground=ACCENT_VOICE)
chat_text.tag_config("ts",    foreground="#555566")

center_btn = tk.Frame(center, bg=DIVIDER)
center_btn.pack(pady=8)

# ── TTS rate slider ───────────────────────────────────────────────────────────
tk.Label(center, text="🔊 Speaker Speed", font=("Arial", 11),
         fg="gray", bg=DIVIDER).pack()
rate_var = tk.IntVar(value=150)
rate_slider = tk.Scale(center, from_=80, to=250, orient="horizontal",
                        variable=rate_var, bg=DIVIDER, fg="white",
                        highlightthickness=0, troughcolor="#333",
                        command=lambda v: update_tts_rate(int(v)))
rate_slider.pack(fill="x", padx=16, pady=4)

volume_var = tk.DoubleVar(value=1.0)
tk.Label(center, text="🔉 Volume", font=("Arial", 11),
         fg="gray", bg=DIVIDER).pack()
vol_slider = tk.Scale(center, from_=0.0, to=1.0, resolution=0.05,
                       orient="horizontal", variable=volume_var,
                       bg=DIVIDER, fg="white", highlightthickness=0,
                       troughcolor="#333",
                       command=lambda v: update_volume(float(v)))
vol_slider.pack(fill="x", padx=16, pady=(0, 10))

# ─────────────────────── RIGHT – Voice Person ─────────────────────────────────
right = tk.Frame(main, bg=CARD_BG, bd=2, relief="ridge")
right.pack(side="left", fill="both", expand=True, padx=(4, 0))

tk.Label(right, text="🎤  VOICE PERSON  (Speech → Text)",
         font=("Arial", 14, "bold"), fg=ACCENT_VOICE, bg=CARD_BG).pack(pady=6)

voice_status = tk.Label(right, text="Status: Ready",
                          font=("Arial", 13), fg="lime", bg=CARD_BG)
voice_status.pack(pady=4)

voice_display = tk.Label(right, text="Speak and it will appear here…",
                           font=("Arial", 22, "bold"), fg="white", bg=CARD_BG,
                           wraplength=400, justify="center")
voice_display.pack(fill="both", expand=True, padx=14, pady=10)

voice_btn_frame = tk.Frame(right, bg=CARD_BG)
voice_btn_frame.pack(pady=10)

continuous_var = tk.BooleanVar(value=False)

# ═════════════════════════════════════════════════════════════════════════════
#  STATE
# ═════════════════════════════════════════════════════════════════════════════
asl_sentence    = ""
current_letter  = ""
start_time      = time.time()
_listening_loop = False   # continuous voice flag
_voice_thread   = None

def update_tts_rate(v):
    global TTS_RATE
    TTS_RATE = v

def update_volume(v):
    global TTS_VOLUME
    TTS_VOLUME = v

# ═════════════════════════════════════════════════════════════════════════════
#  CHAT LOG
# ═════════════════════════════════════════════════════════════════════════════
def add_chat(who: str, text: str):
    """who = 'asl' | 'voice'"""
    ts    = time.strftime("%H:%M")
    label = "✋ ASL" if who == "asl" else "🎤 VOICE"
    chat_text.config(state="normal")
    chat_text.insert("end", f"[{ts}] ", "ts")
    chat_text.insert("end", f"{label}: ", who)
    chat_text.insert("end", text + "\n\n", who)
    chat_text.config(state="disabled")
    chat_text.see("end")

def clear_chat():
    chat_text.config(state="normal")
    chat_text.delete("1.0", "end")
    chat_text.config(state="disabled")

# ═════════════════════════════════════════════════════════════════════════════
#  ASL CONTROLS
# ═════════════════════════════════════════════════════════════════════════════
def asl_speak():
    global asl_sentence
    txt = asl_sentence.strip()
    if not txt:
        return
    add_chat("asl", txt)
    speak_text(txt)
    asl_clear()

def asl_clear():
    global asl_sentence
    asl_sentence = ""
    asl_sentence_var.set("")

def asl_space():
    global asl_sentence
    asl_sentence += " "
    asl_sentence_var.set(asl_sentence)

def asl_backspace():
    global asl_sentence
    asl_sentence = asl_sentence[:-1]
    asl_sentence_var.set(asl_sentence)

tk.Button(asl_btn_frame, text="SPEAK 🔊", font=("Arial", 13, "bold"),
          bg="green", fg="white", width=9, command=asl_speak).pack(side="left", padx=4)
tk.Button(asl_btn_frame, text="SPACE", font=("Arial", 13),
          bg="#555", fg="white", width=6, command=asl_space).pack(side="left", padx=4)
tk.Button(asl_btn_frame, text="⌫", font=("Arial", 13),
          bg="#333", fg="white", width=4, command=asl_backspace).pack(side="left", padx=4)
tk.Button(asl_btn_frame, text="CLEAR", font=("Arial", 13),
          bg="red", fg="white", width=6, command=asl_clear).pack(side="left", padx=4)

# ═════════════════════════════════════════════════════════════════════════════
#  VOICE CONTROLS
# ═════════════════════════════════════════════════════════════════════════════
def do_single_listen():
    voice_status.config(text="Status: 🎤 Listening…", fg="yellow")
    listen_btn.config(state="disabled", bg="#555")
    root.update()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
        voice_status.config(text="Status: Processing…", fg="orange")
        root.update()
        text = recognizer.recognize_google(audio)
        voice_display.config(text=text, fg="white")
        voice_status.config(text="Status: ✅ Done!", fg="lime")
        add_chat("voice", text)
    except sr.WaitTimeoutError:
        voice_status.config(text="Status: ⏱ No speech", fg="red")
    except sr.UnknownValueError:
        voice_status.config(text="Status: ❌ Unclear speech", fg="red")
    except sr.RequestError:
        voice_status.config(text="Status: ❌ Network error", fg="red")
    finally:
        listen_btn.config(state="normal", bg=ACCENT_VOICE)


def continuous_listen_loop():
    """Keep listening until _listening_loop is False."""
    global _listening_loop
    while _listening_loop:
        try:
            voice_status.config(text="Status: 🎤 Continuous…", fg="yellow")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            voice_display.config(text=text, fg="white")
            add_chat("voice", text)
            voice_status.config(text="Status: 🎤 Continuous…", fg="yellow")
        except sr.WaitTimeoutError:
            pass   # just keep looping
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            voice_status.config(text="Status: ❌ Network error", fg="red")
            _listening_loop = False
            break
    voice_status.config(text="Status: Ready", fg="lime")
    continuous_btn.config(text="🔁 Continuous OFF", bg="#333")
    listen_btn.config(state="normal")


def toggle_continuous():
    global _listening_loop, _voice_thread
    if not _listening_loop:
        _listening_loop = True
        listen_btn.config(state="disabled")
        continuous_btn.config(text="⏹ Stop Continuous", bg="red")
        _voice_thread = threading.Thread(target=continuous_listen_loop, daemon=True)
        _voice_thread.start()
    else:
        _listening_loop = False
        continuous_btn.config(text="🔁 Continuous OFF", bg="#333")
        listen_btn.config(state="normal")


def voice_clear():
    voice_display.config(text="Speak and it will appear here…", fg="gray")
    voice_status.config(text="Status: Ready", fg="lime")


listen_btn = tk.Button(voice_btn_frame, text="🎤 LISTEN",
                        font=("Arial", 14, "bold"),
                        bg=ACCENT_VOICE, fg="white", width=11, height=2,
                        command=lambda: threading.Thread(target=do_single_listen, daemon=True).start())
listen_btn.pack(side="left", padx=6)

continuous_btn = tk.Button(voice_btn_frame, text="🔁 Continuous OFF",
                             font=("Arial", 13, "bold"),
                             bg="#333", fg="white", width=15, height=2,
                             command=toggle_continuous)
continuous_btn.pack(side="left", padx=6)

tk.Button(voice_btn_frame, text="🗑 CLEAR",
          font=("Arial", 13, "bold"),
          bg="red", fg="white", width=8, height=2,
          command=voice_clear).pack(side="left", padx=6)

# ── Center bottom buttons ─────────────────────────────────────────────────────
tk.Button(center_btn, text="🗑 Clear Chat", font=("Arial", 13, "bold"),
          bg="#333", fg="white", width=12,
          command=clear_chat).pack(side="left", padx=6)

tk.Button(center_btn, text="❌ Exit", font=("Arial", 13, "bold"),
          bg="#555", fg="white", width=8,
          command=lambda: (cap.release(), root.destroy())).pack(side="left", padx=6)

# ═════════════════════════════════════════════════════════════════════════════
#  CAMERA LOOP  (ASL side)
# ═════════════════════════════════════════════════════════════════════════════
CAM_W, CAM_H = 460, 360

def update_frame():
    global asl_sentence, current_letter, start_time

    ret, frame = cap.read()
    if not ret:
        video_label.after(10, update_frame)
        return

    frame = cv2.flip(frame, 1)
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    hand_result = hands.process(rgb)
    detected_letter = "-"

    if hand_result.multi_hand_landmarks:
        asl_status.config(text="Hand: Detected ✋", fg="lime")
        for hand in hand_result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            if MODEL_LOADED:
                data = []
                for lm in hand.landmark:
                    data += [lm.x, lm.y, lm.z]
                data = np.array(data).reshape(1, -1)
                detected_letter = model.predict(data)[0]

        asl_letter.config(text="Letter: " + detected_letter)

        if detected_letter == current_letter and detected_letter != "-":
            elapsed = time.time() - start_time
            pct = min(int(elapsed / 3.0 * 100), 100)
            filled = int(pct / 10)
            bar = "█" * filled + "░" * (10 - filled)
            hold_progress.config(text=f"Hold: {bar} {pct:3d}%",
                                  fg="lime" if pct >= 100 else "#aaa")

            if elapsed > 3.0:
                # Add space between letters automatically
                if asl_sentence and not asl_sentence.endswith(" "):
                    asl_sentence += " "
                asl_sentence += detected_letter + " "
                asl_sentence_var.set(asl_sentence)
                start_time = time.time()   # reset so they must hold again
        else:
            current_letter = detected_letter
            start_time = time.time()
            hold_progress.config(text="Hold: ░░░░░░░░░░  0%", fg="#777")
    else:
        asl_status.config(text="Hand: No Hand", fg="red")
        asl_letter.config(text="Letter: -")
        hold_progress.config(text="Hold: ░░░░░░░░░░  0%", fg="#555")

    frame_resized = cv2.resize(frame, (CAM_W, CAM_H))
    img   = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    video_label.after(10, update_frame)


update_frame()
root.mainloop()