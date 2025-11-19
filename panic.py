import tkinter as tk
import threading
import random
import time
import simpleaudio as sa
import os
import mysql.connector

# ------------------ MySQL Bağlantısı ------------------
# MySQL veritabanına bağlanıyoruz
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="panic_app"
)
cursor = db.cursor()

# ------------------ GUI Oluşturma ------------------
root = tk.Tk()
root.title("Panic Attack Support App")
root.geometry("400x550")

# Bilgilendirici label
label = tk.Label(
    root, text="Hello! If you feel panic, press 'Start'.", font=("Arial", 12))
label.pack(pady=20)

# Canvas ve daire
canvas = tk.Canvas(root, width=200, height=200)
canvas.pack(pady=20)
circle = canvas.create_oval(80, 80, 120, 120, fill="lightblue")

# Rahatlatıcı mesaj listesi
messages = [
    "This feeling is temporary.",
    "You are safe right now.",
    "Focus on your breathing.",
    "You are not alone.",
    "This too shall pass.",
    "You are stronger than you think.",
    "Take it one moment at a time.",
    "You are doing great.",
    "Breathe in... Breathe out...",
    "You are in control.",
    "You can handle this.",
    "Take a deep breath, it will pass."
]

# WAV dosya yolu
sound_path = os.path.join(os.path.dirname(__file__), "relaxing_sound.wav")

# ------------------ Global Bayraklar ------------------
panic_active = False  # Panic modu başlatılmış mı
panic_paused = False  # Pause durumu
panic_thread = None   # Animasyon thread’i
sound_play_obj = None  # Ses objesi

# ------------------ Güvenli GUI Güncelleme ------------------


def safe_label_update(text):
    """Label güncellemesini ana thread üzerinden yap"""
    root.after(0, lambda: label.config(text=text))


def safe_canvas_update(coords):
    """Canvas koordinat güncellemesini ana thread üzerinden yap"""
    root.after(0, lambda: canvas.coords(circle, *coords))

# ------------------ Ses Fonksiyonları ------------------


def play_relaxing_sound():
    """Rahatlatıcı sesi başlat"""
    global sound_play_obj
    try:
        wave_obj = sa.WaveObject.from_wave_file(sound_path)
        sound_play_obj = wave_obj.play()
    except Exception as e:
        print("Sound error:", e)


def stop_relaxing_sound():
    """Sesi durdur"""
    global sound_play_obj
    try:
        if sound_play_obj:
            sound_play_obj.stop()
            sound_play_obj = None
    except:
        pass

# ------------------ Nefes Animasyonu ------------------


def breath_animation():
    """Sürekli inhale/exhale animasyonu"""
    global panic_active, panic_paused
    while panic_active:
        if panic_paused:
            time.sleep(0.1)
            continue
        # Inhale
        safe_label_update(random.choice(messages))
        for i in range(40, 81, 4):
            if not panic_active:
                return
            while panic_paused:
                time.sleep(0.1)
            safe_canvas_update((100-i, 100-i, 100+i, 100+i))
            time.sleep(0.1)
        time.sleep(0.7)
        # Exhale
        safe_label_update(random.choice(messages))
        for i in range(80, 39, -4):
            if not panic_active:
                return
            while panic_paused:
                time.sleep(0.1)
            safe_canvas_update((100-i, 100-i, 100+i, 100+i))
            time.sleep(0.1)

# ------------------ Panic Modu Kontrol ------------------


def start_panic_mode():
    """Start veya Resume butonu"""
    global panic_active, panic_paused, panic_thread
    if not panic_active:
        panic_active = True
        panic_paused = False
        safe_label_update("Panic mode started!")
        threading.Thread(target=play_relaxing_sound, daemon=True).start()
        panic_thread = threading.Thread(target=breath_animation, daemon=True)
        panic_thread.start()
    elif panic_paused:
        panic_paused = False
        safe_label_update("Panic mode resumed!")
        threading.Thread(target=play_relaxing_sound, daemon=True).start()


def pause_panic_mode():
    """Pause butonu"""
    global panic_paused
    if panic_active and not panic_paused:
        panic_paused = True
        stop_relaxing_sound()
        safe_label_update("Panic mode paused.")

# ------------------ Panic Notları ------------------


def open_log_window():
    """Panik notlarını yaz, listele, sil"""
    log_window = tk.Toplevel(root)
    log_window.title("Panic Attack Log")
    log_window.geometry("500x450")

    tk.Label(log_window, text="Write your notes about your panic attack:",
             font=("Arial", 11)).pack(pady=10)
    text_box = tk.Text(log_window, height=5, width=40)
    text_box.pack(pady=5)

    listbox = tk.Listbox(log_window, width=50)
    listbox.pack(pady=10)

    def load_notes():
        """Notları listele"""
        listbox.delete(0, tk.END)
        cursor.execute(
            "SELECT id, datetime, note FROM panic_logs ORDER BY datetime DESC")
        for row in cursor.fetchall():
            listbox.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]}")

    def save_note():
        """Yeni not kaydet"""
        user_text = text_box.get("1.0", tk.END).strip()
        if user_text:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO panic_logs (datetime, note) VALUES (%s, %s)", (timestamp, user_text))
            db.commit()
            text_box.delete("1.0", tk.END)
            load_notes()

    def delete_note():
        """Seçili notu sil"""
        selected = listbox.curselection()
        if selected:
            note_id = listbox.get(selected[0]).split("|")[0].strip()
            cursor.execute("DELETE FROM panic_logs WHERE id=%s", (note_id,))
            db.commit()
            load_notes()

    save_btn = tk.Button(log_window, text="Save Note",
                         command=save_note, font=("Arial", 12))
    save_btn.pack(pady=5)

    del_btn = tk.Button(log_window, text="Delete Selected Note",
                        command=delete_note, font=("Arial", 12))
    del_btn.pack(pady=5)

    load_notes()


# ------------------ Butonlar ------------------
start_button = tk.Button(root, text="Start / Resume",
                         command=start_panic_mode, font=("Arial", 14))
start_button.pack(pady=10)

pause_button = tk.Button(
    root, text="Pause", command=pause_panic_mode, font=("Arial", 14))
pause_button.pack(pady=10)

log_button = tk.Button(root, text="Write Panic Attack Note",
                       command=open_log_window, font=("Arial", 12))
log_button.pack(pady=10)

root.mainloop()
