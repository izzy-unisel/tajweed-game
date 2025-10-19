import tkinter as tk
import json
import random
import tkinter.font as tkFont
from PIL import Image, ImageTk
from tkinter import ttk

# === THEME SETTINGS ===
THEME = {
    "bg": "#FAF9F6",              # soft cream
    "fg": "#4A4A4A",              # dark gray text
    "accent_pink": "#F7C5CC",     # pastel pink
    "accent_green": "#B4E7C2",    # pastel mint green
    "highlight": "#FCEEF1",       # soft pink highlight
    "button_hover": "#EFB7C1",    # pink hover color
    "button_hover_green": "#A4DDB2",
    "font_family": "Helvetica",
    "question_font_size": 24,
    "option_font_size": 16
}

# ====



# === LOAD DATA ===
def load_flashcards():
    with open('flashcards.json', 'r', encoding='utf-8') as f:
        return json.load(f)["cards"]

# ====



# === WINDOW SETUP ===
window = tk.Tk()
window.title("🌸 Flashcards")
window.geometry("1000x1000")
window.configure(bg=THEME["bg"])

try:
    window.iconbitmap('mecca-3610381_1920.ico')
except Exception:
    pass

# ====



# === FONTS ===
question_font = tkFont.Font(family=THEME["font_family"], size=THEME["question_font_size"], weight='bold')
option_font   = tkFont.Font(family=THEME["font_family"], size=THEME["option_font_size"])

flashcards = load_flashcards()
current_card = 0
selected_option = tk.StringVar()

# ====



# === HEADER IMAGE ===
header_frame = tk.Frame(window, bg=THEME["bg"])
header_frame.pack(fill='x', pady=(20, 10))

# Load image and resize to fit nicely
header_img = Image.open("office-155137_1920.png")
header_img = header_img.resize((200, 150), Image.LANCZOS)
header_photo = ImageTk.PhotoImage(header_img)

# Create centered image label
header_label = tk.Label(header_frame, image=header_photo, bg=THEME["bg"])
header_label.pack(pady=10)

# ====



# === PROGRESS BAR ===
progress_frame = tk.Frame(window, bg=THEME["bg"])
progress_frame.pack(fill='x', padx=80, pady=(5, 20))

style = ttk.Style()
style.theme_use('default')
style.configure(
    "Custom.Horizontal.TProgressbar",
    troughcolor="#FAB7F1",
    background="#FD28BD",
    thickness=20,
    borderwidth=0
)

progress = ttk.Progressbar(
    progress_frame,
    style="Custom.Horizontal.TProgressbar",
    orient='horizontal',
    length=800,
    mode='determinate',
    maximum=len(flashcards)
)
progress.pack(pady=5)

progress_label = tk.Label(
    progress_frame,
    text=f"1 / {len(flashcards)}",
    bg=THEME["bg"],
    fg=THEME["fg"],
    font=(THEME["font_family"], 14)
)
progress_label.pack(pady=5)

# ====



# === SCORE COUNTER (Top-Left) ===
score_frame = tk.Frame(window, bg=THEME["bg"])
score_frame.place(x=20, y=20)  # top-left corner placement

correct_count = 0
wrong_count = 0

correct_label = tk.Label(score_frame, text="0", fg="green", bg=THEME["bg"], font=(THEME["font_family"], 18, "bold"))
slash_label   = tk.Label(score_frame, text="/", fg="black", bg=THEME["bg"], font=(THEME["font_family"], 18, "bold"))
wrong_label   = tk.Label(score_frame, text="0", fg="red", bg=THEME["bg"], font=(THEME["font_family"], 18, "bold"))

correct_label.pack(side="left")
slash_label.pack(side="left")
wrong_label.pack(side="left")

# ====



# === COMPONENT FACTORY HELPERS ===
def make_button(parent, text, bg, hover_bg, command):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=option_font,
        bg=bg,
        fg=THEME["fg"],
        activebackground=hover_bg,
        activeforeground=THEME["fg"],
        relief="flat",
        bd=0,
        padx=20,
        pady=10,
        highlightthickness=0
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    btn.config(cursor="hand2")
    return btn

def make_frame(parent, **kwargs):
    return tk.Frame(parent, bg=THEME["bg"], **kwargs)

# ====



# === QUESTION SECTION ===
question_frame = make_frame(window, height=200)
question_frame.pack(fill='x', padx=40, pady=(40, 20))

question_label = tk.Label(
    question_frame,
    text="",
    font=question_font,
    bg=THEME["bg"],
    fg=THEME["fg"],
    wraplength=900,
    justify='left',
    anchor='nw'
)
question_label.pack(fill='both', expand=True)

resize_job = None  # keep track of pending wrap updates

def adjust_wrap():
    # Use actual question_frame width to prevent flicker
    width = question_frame.winfo_width()
    if width <= 1:
        return  # skip invalid measurements during initial render

    new_wrap = max(300, width - 100)
    question_label.config(wraplength=new_wrap)

def on_resize(event):
    global resize_job
    if resize_job:
        window.after_cancel(resize_job)
    # Delay slightly to wait until user stops resizing
    resize_job = window.after(120, adjust_wrap)

# Bind to window resize
window.bind("<Configure>", on_resize)

# ====



# === OPTIONS SECTION ===
options_frame = make_frame(window)
options_frame.pack(fill='x', padx=60, pady=10)

radio_buttons = []
for _ in range(4):
    rb = tk.Radiobutton(
        options_frame,
        text="",
        variable=selected_option,
        value="",
        font=option_font,
        bg=THEME["bg"],
        fg=THEME["fg"],
        anchor='w',
        justify='left',
        selectcolor=THEME["highlight"],
        activebackground=THEME["highlight"]
    )
    rb.pack(fill='x', padx=20, pady=8)
    radio_buttons.append(rb)

# ====



# === RESULT LABEL ===
result_label = tk.Label(window, text="", font=(THEME["font_family"], 18), bg=THEME["bg"])
result_label.pack(pady=20)

# ====



# === BUTTON BAR ===
btn_frame = make_frame(window)
btn_frame.pack(pady=20)

# ====



# === LOGIC ===

next_button = make_button(
    btn_frame,
    text="Next",
    bg=THEME["accent_green"],
    hover_bg=THEME["button_hover_green"],
    command=lambda: check_and_next()
)
next_button.pack(side='left', padx=15)

def show_card():
    global current_card
    card = flashcards[current_card]
    question_label.config(text=card['question'])
    opts = card['options'].copy()
    random.shuffle(opts)
    selected_option.set("")
    for rb, opt in zip(radio_buttons, opts):
        rb.config(text=opt, value=opt, state='normal')
    for j in range(len(opts), len(radio_buttons)):
        radio_buttons[j].pack_forget()
    result_label.config(text="")

def check_answer():
    global correct_count, wrong_count
    chosen = selected_option.get()
    correct = flashcards[current_card]['answer']
    if chosen.lower() == correct.lower():
        result_label.config(text="🌷 Correct!", fg="green")
        correct_count += 1
    else:
        result_label.config(text=f"🌼 Wrong! The correct answer is “{correct}”", fg="red")
        wrong_count += 1

    # Update score labels
    correct_label.config(text=str(correct_count))
    wrong_label.config(text=str(wrong_count))

def next_flashcard():
    global current_card
    
    current_card = (current_card + 1) % len(flashcards)

    # Update progress bar
    progress['value'] = current_card + 1

    for rb in radio_buttons:
        rb.pack(fill='x', padx=20, pady=8)
    progress_label.config(text=f"{current_card + 1} / {len(flashcards)}")
    show_card()

card_scored = False  # True if the current card has been scored

def check_and_next():
    
    global correct_count, wrong_count, card_scored

    if not card_scored:  # Only score once per card
        chosen = selected_option.get()
        correct = flashcards[current_card]['answer']

        if chosen.lower() == correct.lower():
            result_label.config(text="🌷 Correct!", fg="green")
            correct_count += 1
        else:
            result_label.config(text=f"🌼 Wrong! The correct answer is “{correct}”", fg="red")
            wrong_count += 1

        # Update counters
        correct_label.config(text=str(correct_count))
        wrong_label.config(text=str(wrong_count))

        # Update progress
        progress['value'] = current_card + 1
        progress_label.config(text=f"{current_card + 1} / {len(flashcards)}")

        card_scored = True  # Lock this card

    # Disable the button until next card
    next_button.config(state='disabled')
    window.after(1500, show_next_card) 

def show_next_card():
    global current_card, card_scored
    
    if current_card + 1 >= len(flashcards):
        show_congratulations()
        return  # Stop updating further

    current_card = (current_card + 1) % len(flashcards)
    card_scored = False  # Unlock scoring for the new card

    # Reset radio buttons
    for rb in radio_buttons:
        rb.pack(fill='x', padx=20, pady=8)
    selected_option.set("")
    result_label.config(text="")

    next_button.config(state='normal')  # Re-enable the button
    show_card()

# ====

# === CONGRATULATIONS WINDOW ===

def show_congratulations():
    # Create a new Toplevel window
    congrats_win = tk.Toplevel()
    congrats_win.title("🎉 Congratulations! 🎉")
    congrats_win.geometry("800x600")
    congrats_win.configure(bg=THEME["bg"])
    try:
        congrats_win.iconbitmap('mecca-3610381_1920.ico')
    except Exception:
        pass
    

    # Flower image at the top
    flower_img = Image.open("pansy-427139_1920.png")
    flower_img = flower_img.resize((150, 150), Image.LANCZOS)
    flower_photo = ImageTk.PhotoImage(flower_img)

    img_label = tk.Label(congrats_win, image=flower_photo, bg=THEME["bg"])
    img_label.image = flower_photo  # keep reference
    img_label.pack(pady=20)

    # Congratulations text
    congrats_label = tk.Label(
        congrats_win,
        text="🎉 Congratulations! 🎉",
        font=(THEME["font_family"], 36, "bold"),
        fg="#FD28BD",
        bg=THEME["bg"]
    )
    congrats_label.pack(pady=40)

    # Optional: Show final score
    score_label = tk.Label(
        congrats_win,
        text=f"You got {correct_count} correct and {wrong_count} wrong!",
        font=(THEME["font_family"], 24),
        bg=THEME["bg"]
    )
    score_label.pack(pady=20)

    # Close button
    close_button = make_button(
        congrats_win,
        text="Close",
        bg=THEME["accent_green"],
        hover_bg=THEME["button_hover_green"],
        command=lambda: window.destroy()
    )
    close_button.pack(pady=30)

# ====


# === START APP ===
show_card()
window.mainloop()