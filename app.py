import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import requests
import re
import sys
import os

# === Helper for image path ===
def resource_path(filename):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, "assets", filename)
    except Exception as e:
        print(f"❌ Resource path error: {e}")
        return filename

# === Format AI reply ===
def format_ai_reply(reply):
    formatted = "\n" + reply.strip()
    formatted = re.sub(r'(\d+)\.\s*([^\d]+?)(?=(\d+\.\s)|$)', r'\1. \2\n', formatted)
    formatted = re.sub(r'[•\-]\s*(.*?)\s*(?=[•\-]|$)', r'• \1\n', formatted)
    return formatted.strip()

# === Ask DeepSeek ===
def ask_deepseek(prompt, model="deepseek-r1:1.5b"):
    try:
        url = "http://localhost:11434/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": False}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            raw_text = data.get("response", "No response received.")
            no_think = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)
            clean_text = re.sub(r"[^\x20-\x7E]+", " ", no_think)
            return format_ai_reply(clean_text)
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# === Send logic ===
def send_message(event=None):
    user_input = input_text.get("1.0", tk.END).strip()
    if not user_input:
        return
    input_text.delete("1.0", tk.END)

    chat_text.configure(state="normal", bg=current_chat_bg(), fg=current_text_color())
    chat_text.insert(tk.END, f"\n🧑 You said: {user_input}\n", "user")
    chat_text.see(tk.END)
    chat_text.configure(state="disabled")

    reply = ask_deepseek(user_input)
    chat_text.configure(state="normal", bg=current_chat_bg(), fg=current_text_color())
    chat_text.insert(tk.END, f"🤖 AI said:{reply}\n", "ai")
    chat_text.insert(tk.END, "────────────────────────────\n", "sep")
    chat_text.see(tk.END)
    chat_text.configure(state="disabled")

# === Theme control ===
def current_chat_bg():
    return "#FFFFFF" if ctk.get_appearance_mode() == "Light" else "#1e1e1e"

def current_text_color():
    return "#000000" if ctk.get_appearance_mode() == "Light" else "#FFFFFF"

def toggle_theme():
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("dark")
        theme_button.configure(image=moon_icon)
    else:
        ctk.set_appearance_mode("light")
        theme_button.configure(image=sun_icon)
    chat_text.configure(bg=current_chat_bg(), fg=current_text_color())

# === App Setup ===
ctk.set_default_color_theme("blue")
ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.title("Chatbot")
app.geometry("800x600")
app.minsize(600, 500)
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=1)

# === App Icon ===
try:
    app.iconbitmap(resource_path("robot.ico"))
except Exception as e:
    print(f"⚠️ Icon load error: {e}")

# === Load Icons ===
try:
    sun_icon = ctk.CTkImage(light_image=Image.open(resource_path("sun.png")), size=(24, 24))
    moon_icon = ctk.CTkImage(light_image=Image.open(resource_path("moon.png")), size=(24, 24))
    robot_img = ctk.CTkImage(Image.open(resource_path("robot.png")), size=(40, 40))
except Exception as e:
    print(f"⚠️ Image load error: {e}")
    sun_icon = moon_icon = robot_img = None

# === Top Bar ===
top_bar = ctk.CTkFrame(app, height=60)
top_bar.grid(row=0, column=0, sticky="ew")
top_bar.grid_columnconfigure(1, weight=1)

robot_label = ctk.CTkLabel(top_bar, image=robot_img, text="")
robot_label.grid(row=0, column=0, padx=(10, 5), pady=10)

title_label = ctk.CTkLabel(top_bar, text="Chatbot", font=("Segoe UI", 20, "bold"))
title_label.grid(row=0, column=1, sticky="w", padx=(0, 5))

theme_button = ctk.CTkButton(top_bar, text="", width=36, height=36,
                             image=moon_icon, command=toggle_theme)
theme_button.grid(row=0, column=2, padx=10)

# === Chat Area ===
chat_frame = ctk.CTkFrame(app)
chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 0))
chat_frame.grid_rowconfigure(0, weight=1)
chat_frame.grid_columnconfigure(0, weight=1)

chat_text = tk.Text(chat_frame, bg=current_chat_bg(), fg=current_text_color(),
                    font=("Segoe UI", 13), wrap=tk.WORD,
                    state="disabled", padx=10, pady=10)
chat_text.tag_config("user", foreground="blue", font=("Segoe UI", 13, "bold"))
chat_text.tag_config("ai", foreground="green", font=("Segoe UI", 13))
chat_text.tag_config("sep", foreground="gray")

scrollbar = tk.Scrollbar(chat_frame, command=chat_text.yview)
chat_text['yscrollcommand'] = scrollbar.set

chat_text.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# === Input Area with CTkTextbox ===
input_frame = ctk.CTkFrame(app)
input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
input_frame.grid_columnconfigure(0, weight=4)

input_text = ctk.CTkTextbox(input_frame, height=40)
input_text.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

send_btn = ctk.CTkButton(input_frame, text="Send", command=send_message, width=100, height=40)
send_btn.grid(row=0, column=1, padx=(5, 10), pady=10)

# === Bind Ctrl+Enter to Send ===
input_text.bind("<Control-Return>", send_message)
input_text.bind("<Command-Return>", send_message)  # for macOS

app.mainloop()
