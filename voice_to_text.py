import tkinter as tk
import speech_recognition as sr
import threading

recognizer = sr.Recognizer()

# ── Window ────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Voice to Text - For Hearing Impaired")
root.configure(bg="#1e1e1e")
root.state("zoomed")

# ── Title ─────────────────────────────────────────────────────────────────────
tk.Label(root,
         text="🎤 VOICE TO TEXT",
         font=("Arial", 28, "bold"),
         fg="white", bg="#1e1e1e").pack(pady=20)

tk.Label(root,
         text="Press LISTEN and speak clearly",
         font=("Arial", 16),
         fg="gray", bg="#1e1e1e").pack()

# ── Status label ──────────────────────────────────────────────────────────────
status_label = tk.Label(root,
                         text="Status: Ready",
                         font=("Arial", 18),
                         fg="lime", bg="#1e1e1e")
status_label.pack(pady=15)

# ── Big text display box ──────────────────────────────────────────────────────
text_frame = tk.Frame(root, bg="#2d2d2d", bd=3, relief="ridge")
text_frame.pack(fill="both", expand=True, padx=40, pady=10)

text_display = tk.Label(text_frame,
                         text="Text will appear here...",
                         font=("Arial", 42, "bold"),
                         fg="white", bg="#2d2d2d",
                         wraplength=1200,
                         justify="center",
                         anchor="center")
text_display.pack(fill="both", expand=True, padx=20, pady=20)

# ── History box ───────────────────────────────────────────────────────────────
tk.Label(root,
         text="History:",
         font=("Arial", 14),
         fg="gray", bg="#1e1e1e").pack(anchor="w", padx=40)

history_box = tk.Text(root,
                       font=("Arial", 14),
                       fg="cyan", bg="#1a1a1a",
                       height=5,
                       state="disabled",
                       wrap="word")
history_box.pack(fill="x", padx=40, pady=5)

# ── Buttons ───────────────────────────────────────────────────────────────────
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=15)

history_text = []


def add_to_history(text):
    history_text.append(text)
    history_box.config(state="normal")
    history_box.delete("1.0", tk.END)
    history_box.insert(tk.END, "\n".join(history_text[-6:]))
    history_box.config(state="disabled")
    history_box.see(tk.END)


def listen():
    status_label.config(text="Status: 🎤 Listening...", fg="yellow")
    listen_btn.config(state="disabled", bg="#555555")
    root.update()

    def do_listen():
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            status_label.config(text="Status: Processing...", fg="orange")
            root.update()

            text = recognizer.recognize_google(audio)
            text_display.config(text=text, fg="white")
            status_label.config(text="Status: ✅ Done!", fg="lime")
            add_to_history(text)

        except sr.WaitTimeoutError:
            status_label.config(text="Status: ⏱ No speech detected", fg="red")
            text_display.config(text="No speech detected.\nTry again.", fg="red")

        except sr.UnknownValueError:
            status_label.config(text="Status: ❌ Could not understand", fg="red")
            text_display.config(text="Could not understand.\nSpeak clearly.", fg="red")

        except sr.RequestError:
            status_label.config(text="Status: ❌ Network error", fg="red")
            text_display.config(text="Network error.\nCheck internet.", fg="red")

        finally:
            listen_btn.config(state="normal", bg="#1e90ff")

    thread = threading.Thread(target=do_listen)
    thread.daemon = True
    thread.start()


def clear_text():
    text_display.config(text="Text will appear here...", fg="gray")
    status_label.config(text="Status: Ready", fg="lime")


def close_app():
    root.destroy()


listen_btn = tk.Button(btn_frame,
                        text="🎤  LISTEN",
                        font=("Arial", 20, "bold"),
                        bg="#1e90ff", fg="white",
                        width=12, height=2,
                        command=listen)
listen_btn.pack(side="left", padx=15)

tk.Button(btn_frame,
          text="🗑  CLEAR",
          font=("Arial", 20, "bold"),
          bg="red", fg="white",
          width=12, height=2,
          command=clear_text).pack(side="left", padx=15)

tk.Button(btn_frame,
          text="❌  EXIT",
          font=("Arial", 20, "bold"),
          bg="gray", fg="white",
          width=12, height=2,
          command=close_app).pack(side="left", padx=15)

root.mainloop()