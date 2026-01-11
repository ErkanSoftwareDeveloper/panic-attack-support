# 🧘 Panic Attack Support App

A **desktop application for managing panic attacks**, built with **Python**, **Tkinter**, and **MySQL**.
This app helps users calm down with **breathing animations**, **relaxing sounds**, and **motivational messages**, while also allowing logging of panic events.

---

## ✨ Features

* Start/resume panic support mode with breathing animation
* Pause panic mode at any time
* Plays relaxing sound during panic mode
* Motivational messages displayed dynamically
* Log panic attacks and personal notes
* View, save, and delete panic notes from MySQL
* Animated breathing circle to guide inhaling and exhaling
* Threaded operations for smooth UI

---

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter** – GUI framework
* **Threading** – responsive animation and sound
* **MySQL** – store panic notes
* **Subprocess** – play sound files
* **OS / Time / Random** – supporting functionality

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/ErkanSoftwareDeveloper/panic-attack-support.git
cd panic-attack-support
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up MySQL database with the provided `panic.sql` script:

```sql
CREATE DATABASE IF NOT EXISTS panic_app

USE panic_app;

CREATE TABLE IF NOT EXISTS panic_logs (
	id iNT AUTO_INCREMENT primary key,
	datetime VARCHAR(50) NOT NULL,
	note TEXT NOT NULL
);

SELECT * FROM panic_logs pl;
```

Place a relaxing sound file named `relaxing_sound.wav` in the project folder.

---

## ▶️ Usage

Run the application:

```bash
python panic.py
```

1. Press **Start / Resume** to begin panic mode
2. Press **Pause** to stop animations and sound
3. Press **Write Panic Attack Note** to open the log window
4. Add notes about your panic attacks and save them to the database
5. Delete notes if needed from the log window

---

## 📁 Project Structure

```text
panic-attack-support/
├─ panic.py       # Main application file
├─ relaxing_sound.wav # Relaxing sound for breathing exercises
├─ panic.sql          # SQL script to create MySQL database & table
├─ .gitignore         # Git ignored files
├─ README.md          # Project documentation
└─ requirements.txt   # Project dependencies
```

---

## 📸 Video

![ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/7b5f8d26-cef8-48ec-bd1e-61e307c626be)


---

## 🚀 Possible Improvements

* Cross-platform sound playback support
* Customizable breathing patterns
* Save user preferences for messages and animation speed
* Dark/light theme for UI
* Packaging as executable (.exe / .app)

---

## 📄 License

This project is intended for **educational and personal use**.
