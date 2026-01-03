import tkinter as tk  # Import Tkinter for GUI elements
import threading  # Import threading to run tasks in parallel (animations, sounds)
import random  # Import random to select random messages
import time  # Import time for sleep/delay functions
import os  # Import os for handling file paths
import subprocess  # Import subprocess to run external commands (play sound)
import mysql.connector  # Import MySQL connector to interact with MySQL database

# ------------------ MySQL Connection ------------------
db = mysql.connector.connect(
    host="localhost",  # MySQL server host
    user="root",       # MySQL username
    password="",       # MySQL password
    database="panic_app"  # Database name
)  # Establish connection to MySQL
cursor = db.cursor()  # Create cursor object to execute SQL queries

# ------------------ Sound Control ------------------
sound_path = os.path.join(os.path.dirname(__file__), "relaxing_sound.wav")  # Full path to WAV file
sound_process = None  # Variable to store subprocess playing sound
sound_lock = threading.Lock()  # Lock to prevent race conditions when starting/stopping sound

def start_relaxing_sound():
    """Start playing relaxing sound if not already playing."""
    global sound_process
    with sound_lock:  # Ensure thread safety
        if sound_process and sound_process.poll() is None:  # Check if already running
            return  # Do nothing if sound is already playing
        sound_process = subprocess.Popen(["afplay", sound_path])  # Start sound using afplay (macOS)

def stop_relaxing_sound():
    """Stop relaxing sound if it is currently playing."""
    global sound_process
    with sound_lock:  # Ensure thread safety
        if sound_process and sound_process.poll() is None:  # Check if process is active
            sound_process.terminate()  # Stop the sound
            sound_process = None  # Reset variable

# ------------------ GUI Setup ------------------
root = tk.Tk()  # Create main application window
root.title("Panic Attack Support App")  # Set window title
root.geometry("400x550")  # Set window size

label = tk.Label(root, text="Hello! If you feel panic, press 'Start'.", font=("Arial", 12))  # Instruction label
label.pack(pady=20)  # Add label with vertical padding

canvas = tk.Canvas(root, width=200, height=200)  # Create canvas for breathing circle
canvas.pack(pady=20)  # Add canvas with padding
circle = canvas.create_oval(80, 80, 120, 120, fill="lightblue")  # Draw initial circle

# ------------------ Motivational Messages ------------------
messages = [
    "This feeling is temporary.",  # Message 1
    "You are safe right now.",     # Message 2
    "Focus on your breathing.",    # Message 3
    "You are not alone.",          # Message 4
    "This too shall pass.",        # Message 5
    "You are stronger than you think.",  # Message 6
    "Take it one moment at a time.",      # Message 7
    "You are doing great.",        # Message 8
    "Breathe in... Breathe out...",  # Message 9
    "You are in control.",         # Message 10
    "You can handle this.",        # Message 11
    "Take a deep breath, it will pass."  # Message 12
]  # List of calming messages

# ------------------ Global Flags ------------------
panic_active = False  # Flag to indicate if panic mode is running
panic_paused = False  # Flag to indicate if panic mode is paused
panic_thread = None  # Thread that will run the breathing animation

# ------------------ Safe GUI Updates ------------------
def safe_label_update(text):
    """Update label text safely from another thread."""
    root.after(0, lambda: label.config(text=text))  # Schedule update in main Tkinter thread

def safe_canvas_update(coords):
    """Update circle coordinates safely from another thread."""
    root.after(0, lambda: canvas.coords(circle, *coords))  # Schedule canvas update

# ------------------ Breathing Animation ------------------
def breath_animation():
    """Animate breathing circle with inhale and exhale while showing messages."""
    global panic_active, panic_paused
    while panic_active:  # Loop as long as panic mode is active
        if panic_paused:  # Skip animation if paused
            time.sleep(0.1)
            continue

        # ------------------ Inhale ------------------
        safe_label_update(random.choice(messages))  # Display random message
        for i in range(40, 81, 4):  # Gradually expand circle
            if not panic_active:  # Stop if panic mode ends
                return
            while panic_paused:  # Pause if needed
                time.sleep(0.1)
            safe_canvas_update((100-i, 100-i, 100+i, 100+i))  # Update circle coordinates
            time.sleep(0.1)  # Delay for smooth animation
        time.sleep(0.7)  # Hold at full inhale

        # ------------------ Exhale ------------------
        safe_label_update(random.choice(messages))  # Display random message
        for i in range(80, 39, -4):  # Gradually shrink circle
            if not panic_active:
                return
            while panic_paused:
                time.sleep(0.1)
            safe_canvas_update((100-i, 100-i, 100+i, 100+i))  # Update circle coordinates
            time.sleep(0.1)  # Delay for smooth animation

# ------------------ Panic Mode Controls ------------------
def start_panic_mode():
    """Start or resume panic mode with sound and animation."""
    global panic_active, panic_paused, panic_thread
    if not panic_active:  # If not started yet
        panic_active = True
        panic_paused = False
        safe_label_update("Panic mode started!")  # Update label
        start_relaxing_sound()  # Start sound
        panic_thread = threading.Thread(target=breath_animation, daemon=True)  # Start animation thread
        panic_thread.start()
    elif panic_paused:  # Resume if paused
        panic_paused = False
        safe_label_update("Panic mode resumed!")  # Update label
        start_relaxing_sound()  # Resume sound

def pause_panic_mode():
    """Pause panic mode and stop sound."""
    global panic_paused
    if panic_active and not panic_paused:  # Only if running
        panic_paused = True
        safe_label_update("Panic mode paused.")  # Update label
        stop_relaxing_sound()  # Stop sound

# ------------------ Panic Notes Window ------------------
def open_log_window():
    """Open a window to write, view, and delete panic notes in MySQL."""
    log_window = tk.Toplevel(root)  # Create new window
    log_window.title("Panic Attack Log")  # Set title
    log_window.geometry("500x450")  # Set size

    tk.Label(log_window, text="Write your notes about your panic attack:", font=("Arial", 11)).pack(pady=10)
    text_box = tk.Text(log_window, height=5, width=40)  # Text area for user notes
    text_box.pack(pady=5)

    listbox = tk.Listbox(log_window, width=50)  # List of previous notes
    listbox.pack(pady=10)

    # ------------------ Load Notes ------------------
    def load_notes():
        """Load notes from database and display in listbox."""
        listbox.delete(0, tk.END)
        cursor.execute("SELECT id, datetime, note FROM panic_logs ORDER BY datetime DESC")
        for row in cursor.fetchall():
            listbox.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]}")  # Display note with ID and timestamp

    # ------------------ Save Note ------------------
    def save_note():
        """Save new note to database."""
        user_text = text_box.get("1.0", tk.END).strip()  # Get text from Text widget
        if user_text:  # Only if not empty
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp
            cursor.execute("INSERT INTO panic_logs (datetime, note) VALUES (%s, %s)", (timestamp, user_text))
            db.commit()  # Commit changes
            text_box.delete("1.0", tk.END)  # Clear text box
            load_notes()  # Refresh list

    # ------------------ Delete Note ------------------
    def delete_note():
        """Delete selected note from database."""
        selected = listbox.curselection()
        if selected:  # Only if something selected
            note_id = listbox.get(selected[0]).split("|")[0].strip()  # Extract note ID
            cursor.execute("DELETE FROM panic_logs WHERE id=%s", (note_id,))
            db.commit()
            load_notes()  # Refresh list

    save_btn = tk.Button(log_window, text="Save Note", command=save_note, font=("Arial", 12))
    save_btn.pack(pady=5)  # Save button

    del_btn = tk.Button(log_window, text="Delete Selected Note", command=delete_note, font=("Arial", 12))
    del_btn.pack(pady=5)  # Delete button

    load_notes()  # Load notes on window open

# ------------------ Main Buttons ------------------
start_button = tk.Button(root, text="Start / Resume", command=start_panic_mode, font=("Arial", 14))
start_button.pack(pady=10)  # Button to start or resume panic mode

pause_button = tk.Button(root, text="Pause", command=pause_panic_mode, font=("Arial", 14))
pause_button.pack(pady=10)  # Button to pause panic mode

log_button = tk.Button(root, text="Write Panic Attack Note", command=open_log_window, font=("Arial", 12))
log_button.pack(pady=10)  # Button to open notes window

root.mainloop()  # Start Tkinter event loop
