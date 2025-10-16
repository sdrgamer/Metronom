import numpy as np
import pygame
import tkinter as tk
import threading
import time
from datetime import datetime

pygame.mixer.init(frequency=44100, size=-16, channels=2)

frequency = 1000
accent_frequency = 1500
duration = 100
sample_rate = 44100
click_volume = 0.5
accent_volume = 0.8

t = np.linspace(0, duration/1000, int(sample_rate*duration/1000), False)
tone = np.sin(frequency * t * 2 * np.pi)
tone = (tone * 32767).astype(np.int16)
tone_stereo = np.column_stack((tone, tone))

accent_tone = np.sin(accent_frequency * t * 2 * np.pi)
accent_tone = (accent_tone * 32767).astype(np.int16)
accent_stereo = np.column_stack((accent_tone, accent_tone))

click_sound = pygame.sndarray.make_sound(tone_stereo)
click_sound.set_volume(click_volume)
accent_sound = pygame.sndarray.make_sound(accent_stereo)
accent_sound.set_volume(accent_volume)

running = False
theme_dark = True
accent_enabled = True
click_count = 0  # for Easter egg

def flash_beat(color1, color2, duration=0.05):
    beat_label.config(fg=color1)
    root.update()
    time.sleep(duration)
    beat_label.config(fg=color2)

def start_metronome():
    global running
    try:
        bpm_val = int(bpm_entry.get())
        beats_val = beats_entry.get()
        measure_val = measure_entry.get()
        beats_val = int(beats_val) if beats_val.strip() != "" and int(beats_val) > 0 else None
        measure_val = int(measure_val) if measure_val.strip() != "" and int(measure_val) > 0 else 4
        interval = 60 / bpm_val
    except ValueError:
        status_label.config(text="Please enter valid numbers!")
        return

    running = True
    status_label.config(text="Countdown...")

    def play_loop():
        for i in range(4, 0, -1):
            if not running: return
            status_label.config(text=f"Starting in {i}")
            click_sound.play()
            flash_beat("white", "red", 0.1)
            time.sleep(interval)
        status_label.config(text="Running...")

        i = 0
        while running and (beats_val is None or i < beats_val):
            if accent_enabled and i % measure_val == 0:
                accent_sound.play()
                flash_beat("yellow", "red")
            else:
                click_sound.play()
                flash_beat("red", "yellow")
            beat_label.config(text=f"Beat: {i+1}" + (f"/{beats_val}" if beats_val else ""))
            time_label.config(text=datetime.now().strftime("%H:%M:%S"))
            i += 1
            time.sleep(interval)
        if running:
            status_label.config(text="Finished")
        else:
            status_label.config(text="Stopped")
        beat_label.config(text="", fg="red")

    threading.Thread(target=play_loop).start()

def stop_metronome():
    global running
    running = False

def toggle_theme():
    global theme_dark
    theme_dark = not theme_dark
    bg_color = "#1e1e1e" if theme_dark else "#f0f0f0"
    fg_color = "white" if theme_dark else "black"
    root.configure(bg=bg_color)
    frame.configure(bg=bg_color)
    for widget in frame.winfo_children():
        try:
            widget.configure(bg=bg_color, fg=fg_color)
        except:
            pass

def toggle_accent():
    global accent_enabled
    accent_enabled = not accent_enabled
    accent_button.config(text=f"Accent: {'ON' if accent_enabled else 'OFF'}")

def update_click_volume(val):
    click_sound.set_volume(float(val)/100)

def update_accent_volume(val):
    accent_sound.set_volume(float(val)/100)

def set_bpm(p):
    bpm_entry.delete(0, tk.END)
    bpm_entry.insert(0, str(p))

# --- Easter Egg Snake Game ---
def launch_snake_game():
    snake_win = tk.Toplevel(root)
    snake_win.title("🐍 Snake Easter Egg 🐍")
    snake_win.geometry("400x400")
    canvas = tk.Canvas(snake_win, width=400, height=400, bg="black")
    canvas.pack()

    snake = [(20,20)]
    direction = "Right"
    square_size = 20
    import random
    food = (random.randint(0,19)*square_size, random.randint(0,19)*square_size)

    def draw():
        canvas.delete("all")
        for x,y in snake:
            canvas.create_rectangle(x, y, x+square_size, y+square_size, fill="green")
        fx, fy = food
        canvas.create_rectangle(fx, fy, fx+square_size, fy+square_size, fill="red")

    def move_snake():
        nonlocal snake, food
        x, y = snake[0]
        if direction == "Up": y -= square_size
        if direction == "Down": y += square_size
        if direction == "Left": x -= square_size
        if direction == "Right": x += square_size
        new_head = (x,y)
        snake = [new_head] + snake[:-1]

        if new_head == food:
            snake.append(snake[-1])
            food = (random.randint(0,19)*square_size, random.randint(0,19)*square_size)

        if not (0 <= x < 400 and 0 <= y < 400):
            snake_win.destroy()
            return

        draw()
        snake_win.after(200, move_snake)

    def change_direction(event):
        nonlocal direction
        if event.keysym in ["Up","Down","Left","Right"]:
            direction = event.keysym

    snake_win.bind("<Key>", change_direction)
    snake_win.focus_set()
    move_snake()

# --- Info Window with hidden Easter Egg ---
def show_info():
    global click_count
    info_win = tk.Toplevel(root)
    info_win.title("Info")
    info_win.geometry("400x200")
    info_win.configure(bg="#1e1e1e" if theme_dark else "#f0f0f0")
    fg_color = "white" if theme_dark else "black"

    def secret_click(event=None):
        global click_count
        click_count += 1
        if click_count >= 5:
            info_win.destroy()
            launch_snake_game()
            click_count = 0

    info_label = tk.Label(info_win, text="CREATOR: SDR", font=("Arial", 16),
                          bg=info_win["bg"], fg=fg_color)
    info_label.pack(pady=5)
    info_label.bind("<Button-1>", secret_click)

    tk.Label(info_win, text=f"DATE: {datetime.now().strftime('%Y-%m-%d')}",
             font=("Arial", 16), bg=info_win["bg"], fg=fg_color).pack(pady=5)
    tk.Label(info_win, text="Thanks for using our tool :)",
             font=("Arial", 16), bg=info_win["bg"], fg=fg_color).pack(pady=5)
    tk.Button(info_win, text="Close", command=info_win.destroy,
              bg="#007acc", fg="white").pack(pady=10)

# --- Main Window ---
root = tk.Tk()
root.title("Pro Metronome")
root.geometry("1000x800")
root.configure(bg="#1e1e1e")

frame = tk.Frame(root, bg="#1e1e1e")
frame.place(relx=0.5, rely=0.5, anchor="center")

label_font = ("Arial", 25, "bold")
entry_font = ("Arial", 18)
button_font = ("Arial", 18, "bold")

# Input Fields
tk.Label(frame, text="BPM:", font=label_font, fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=10, pady=5)
bpm_entry = tk.Entry(frame, font=entry_font, width=5)
bpm_entry.insert(0, "100")
bpm_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Beats:", font=label_font, fg="white", bg="#1e1e1e").grid(row=1, column=0, padx=10, pady=5)
beats_entry = tk.Entry(frame, font=entry_font, width=5)
beats_entry.insert(0, "16")
beats_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Beats per Measure:", font=label_font, fg="white", bg="#1e1e1e").grid(row=2, column=0, padx=10, pady=5)
measure_entry = tk.Entry(frame, font=entry_font, width=5)
measure_entry.insert(0, "4")
measure_entry.grid(row=2, column=1, padx=10, pady=5)

# Buttons
start_button = tk.Button(frame, text="Start", font=button_font, fg="white", bg="#007acc", command=start_metronome)
start_button.grid(row=3, column=0, pady=10, padx=10)
stop_button = tk.Button(frame, text="Stop", font=button_font, fg="white", bg="#cc0000", command=stop_metronome)
stop_button.grid(row=3, column=1, pady=10, padx=10)

theme_button = tk.Button(frame, text="Toggle Theme", font=button_font, fg="white", bg="#555555", command=toggle_theme)
theme_button.grid(row=4, column=0, pady=5, padx=10)
accent_button = tk.Button(frame, text="Accent: ON", font=button_font, fg="white", bg="#555555", command=toggle_accent)
accent_button.grid(row=4, column=1, pady=5, padx=10)

# Info Button top-left
info_button = tk.Button(root, text="Info", font=button_font, fg="white", bg="#555555", command=show_info)
info_button.place(x=10, y=10)

# Status & Beat Display
status_label = tk.Label(frame, text="", font=("Arial", 20), fg="yellow", bg="#1e1e1e")
status_label.grid(row=6, column=0, columnspan=2, pady=5)
beat_label = tk.Label(frame, text="", font=("Arial", 50, "bold"), fg="red", bg="#1e1e1e")
beat_label.grid(row=7, column=0, columnspan=2, pady=20)
time_label = tk.Label(frame, text="", font=("Arial", 18), fg="white", bg="#1e1e1e")
time_label.grid(row=8, column=0, columnspan=2, pady=5)

# Volume Sliders
click_vol_slider = tk.Scale(frame, from_=0, to=100, orient="horizontal", label="Click Volume", command=update_click_volume)
click_vol_slider.set(int(click_volume*100))
click_vol_slider.grid(row=9, column=0, pady=5, padx=10)
accent_vol_slider = tk.Scale(frame, from_=0, to=100, orient="horizontal", label="Accent Volume", command=update_accent_volume)
accent_vol_slider.set(int(accent_volume*100))
accent_vol_slider.grid(row=9, column=1, pady=5, padx=10)

# BPM Presets
preset_frame = tk.Frame(frame, bg="#1e1e1e")
preset_frame.grid(row=10, column=0, columnspan=2, pady=10)
for idx, tempo in enumerate([60, 80, 100, 120]):
    tk.Button(preset_frame, text=f"{tempo} BPM", font=("Arial", 14), command=lambda t=tempo: set_bpm(t)).grid(row=0, column=idx, padx=5)

root.mainloop()
