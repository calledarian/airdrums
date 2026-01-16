# 🥁 Air Drum Kit - Interactive Computer Vision Drum Set

**Created by:** Arian Khademolghorani  

The **Air Drum Kit** is a virtual drumming application that turns your webcam into a musical instrument. Using Computer Vision (OpenCV) and Color Tracking, it allows you to play drums in mid-air using any blue object—like a blue marker, a drumstick with blue tape, or even a blue toy.

---

## ✨ Features

* **Real-time Color Tracking:** Uses HSV color filtering to track blue objects with precision.
* **Virtual Overlay:** Visualizes drum pads (Snare, Kick, Hi-Hat, Toms, Crash) directly on your video feed.
* **Visual Feedback:** Drums light up with a red tint when struck.
* **Low-Latency Audio:** Uses Pygame Mixer for responsive sound triggering.
* **Menu System:** Integrated Main Menu and Credits screen.

---

## 🛠️ Prerequisites

To run this project, you need **Python 3.x** installed on your machine along with a webcam.

### Required Libraries
Install the dependencies using `pip`:

```bash
pip install opencv-python numpy pygame

```

---

## 📂 Project Structure

**Important:** For the code to run successfully, your file and folder structure must look exactly like this. The application relies on specific paths to load images and sounds.

```text
Air-Drum-Kit/
│
├── main.py       # The main Python script
├── README.md             # This file
│
└── assets/
    ├── Samples/          # Audio files (.wav)
    │   ├── kick-808.wav
    │   ├── snare-808.wav
    │   ├── openhat-808.wav
    │   ├── tom-acoustic01.wav
    │   ├── tom-acoustic02.wav
    │   └── crash-808.wav
    │
    └── images/           # Visual assets (.png)
        ├── kick_drum.png
        ├── snare_drum.png
        ├── hi_hat.png
        ├── tom.png
        └── crash_cymbal.png

```
---

## 🚀 How to Run

1. Connect your webcam.
2. Navigate to the project folder in your terminal.
3. Run the script:
```bash
python main.py

```


4. The application will open in the **Main Menu**.

---

## 🎮 Controls & Usage

### The "Drumstick"

This application is tuned to detect **BLUE** objects.

* **Best Results:** Use a bright blue marker cap, a blue fidget spinner, or wrap blue electrical tape around a pen/stick.
* **Lighting:** Ensure your room is well-lit so the camera can distinguish the blue color.

### Keyboard Controls

| Key | Action |
| --- | --- |
| **P** | **Play Mode** (Start Drumming) |
| **C** | View **Credits** |
| **B** | **Back** to Main Menu |
| **Q** | **Quit** / Exit Application |

---

## ⚙️ Configuration

You can tweak the settings inside the `air_drum_kit.py` file:

* **Window Size:** Modify `WINDOW_WIDTH` and `WINDOW_HEIGHT` (Default: 640x480).
* **Color Sensitivity:** If your blue object isn't being detected, adjust the HSV values:
```python
BLUE_LOWER_BOUND = np.array([90, 50, 20])
BLUE_UPPER_BOUND = np.array([140, 255, 255])

```



---

## 🤝 Credits

* **Developer:** Arian Khademolghorani
* **Art/Drawings:** Ceylin Ipek Ak
* **Audio Samples:** [99Sounds](https://99sounds.org/)
* **Libraries:** OpenCV, Pygame, NumPy

---

## 📝 License

This project is open-source. Feel free to modify and improve it!
