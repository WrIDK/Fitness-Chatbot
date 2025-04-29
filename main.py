# main.py

import customtkinter as ctk
from PIL import Image
from ollama_api import stream_ollama
from prompts import SYSTEM_PROMPTS
import threading
import time

# Set appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FitnessChatbotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Fit-Track")
        self.geometry("750x750")
        self.minsize(700, 700)

        self.selected_style = "Coach"
        self.chat_history = []
        self.stop_generating = False
        self.generating_thread = None

        self.create_widgets()

    def create_widgets(self):
        # ===== Logo Image =====
        self.logo_image = ctk.CTkImage(
            light_image=Image.open(
                r"your image location.png"
            ),
            size=(245, 100)
        )
        self.logo_label = ctk.CTkLabel(self, image=self.logo_image, text="")
        self.logo_label.pack(pady=(10, 5))

        # ===== Title =====
        self.title_label = ctk.CTkLabel(self, text='''Fit-Track
Offline Fitness Chatbot''', font=("Helvetica", 26, "bold"))
        self.title_label.pack(pady=20)

        # ===== Style Option Menu =====
        self.style_option = ctk.CTkOptionMenu(self, values=list(SYSTEM_PROMPTS.keys()), command=self.change_style)
        self.style_option.set("Coach")
        self.style_option.pack(pady=10)

        # ===== Chat Frame =====
        self.chat_frame = ctk.CTkScrollableFrame(self, width=650, height=500)
        self.chat_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # ===== Input Frame =====
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", pady=10, padx=20)

        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message...", width=400)
        self.user_input.pack(pady=10, padx=(10, 5), side="left", expand=True, fill="x")

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(padx=(5, 5), pady=10, side="left")

        self.stop_button = ctk.CTkButton(self.input_frame, text="Stop", command=self.stop_response, fg_color="red")
        self.stop_button.pack(padx=(5, 10), pady=10, side="left")

    def change_style(self, new_style):
        self.selected_style = new_style
        self.chat_history.clear()

    def display_message(self, sender, message, is_user=False, is_stream=False):
        bubble_color = "#1f6aa5" if is_user else "#3a3a3a"
        text_color = "white"

        frame = ctk.CTkFrame(self.chat_frame, fg_color=bubble_color, corner_radius=15)
        frame.pack(pady=5, padx=10, anchor="e" if is_user else "w")

        label = ctk.CTkLabel(frame, text=message, text_color=text_color, wraplength=500, justify="left", anchor="w")
        label.pack(padx=10, pady=5)

        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)  # Auto-scroll to bottom ✅
        return label

    def update_message(self, label, new_text):
        label.configure(text=new_text)
        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)  # Auto-scroll to bottom ✅

    def build_prompt(self, user_message):
        system_prompt = SYSTEM_PROMPTS.get(self.selected_style, "")
        history = "\n".join([f"{sender}: {msg}" for sender, msg in self.chat_history])
        full_prompt = f"{system_prompt}\n{history}\nUser: {user_message}\nAssistant:"
        return full_prompt

    def send_message(self):
        user_msg = self.user_input.get().strip()
        if user_msg == "":
            return

        self.display_message("You", user_msg, is_user=True)
        self.chat_history.append(("User", user_msg))

        self.user_input.delete(0, "end")

        full_prompt = self.build_prompt(user_msg)

        self.stop_generating = False
        self.generating_thread = threading.Thread(target=self.get_bot_response, args=(full_prompt,), daemon=True)
        self.generating_thread.start()

    def get_bot_response(self, full_prompt):
        bot_label = self.display_message("FitnessBot", "", is_user=False, is_stream=True)

        bot_message = ""
        for part in stream_ollama(full_prompt):
            if self.stop_generating:
                break
            bot_message += part
            self.update_message(bot_label, bot_message)
            time.sleep(0.02)  # Typing effect

        if not self.stop_generating:
            self.chat_history.append(("Assistant", bot_message))
        else:
            self.update_message(bot_label, bot_message + "\n\n[Response stopped]")

    def stop_response(self):
        self.stop_generating = True

if __name__ == "__main__":
    app = FitnessChatbotApp()
    app.mainloop()
