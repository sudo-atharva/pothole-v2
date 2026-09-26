"""
Tkinter GUI for road damage assessment.
Runs YOLO segmentation on a webcam or video file and shows the smoothed damage %.
Tick "GPS survey" to also log geotagged pothole images/CSV via the ESP32 (see road_survey.py).

Run:  python gui_app.py
"""
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from collections import deque

import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO

import road_survey as rs

DISPLAY_SIZE = (960, 540)  # max size of the video preview


class App:
    def __init__(self, root):
        self.root = root
        self.model = None
        self.thread = None
        self.running = False
        self.frame = None  # latest annotated RGB frame, handed from worker to UI
        self.status = 'Pick a source and press Start.'

        root.title('Road Damage Assessment')
        ctrl = ttk.Frame(root, padding=8)
        ctrl.pack(fill='x')

        ttk.Label(ctrl, text='Source (camera index or video file):').pack(side='left')
        self.source = tk.StringVar(value=str(rs.CAMERA_INDEX))
        ttk.Entry(ctrl, textvariable=self.source, width=40).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Browse...', command=self.browse).pack(side='left')

        self.survey = tk.BooleanVar()
        ttk.Checkbutton(ctrl, text='GPS survey on port', variable=self.survey).pack(side='left', padx=(12, 4))
        self.port = tk.StringVar(value=rs.SERIAL_PORT)
        ttk.Entry(ctrl, textvariable=self.port, width=8).pack(side='left')

        self.start_btn = ttk.Button(ctrl, text='Start', command=self.toggle)
        self.start_btn.pack(side='left', padx=12)

        self.video = ttk.Label(root)
        self.video.pack()
        self.info = ttk.Label(root, padding=8, font=('Segoe UI', 12))
        self.info.pack(fill='x')

        root.protocol('WM_DELETE_WINDOW', self.close)
        self.refresh()

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[('Video', '*.mp4 *.avi *.mov *.mkv'), ('All files', '*.*')])
        if path:
            self.source.set(path)

    def toggle(self):
        if self.running:
            self.running = False
            return
        if self.thread and self.thread.is_alive():
            return  # previous run still shutting down
        src = self.source.get().strip()
        src = int(src) if src.isdigit() else src
        port = self.port.get().strip() if self.survey.get() else None
        self.running = True
        self.thread = threading.Thread(target=self.worker, args=(src, port), daemon=True)
        self.thread.start()

    def worker(self, source, port):
        cap = cv2.VideoCapture(source)
        gps = None
        try:
            if not cap.isOpened():
                self.status = f'Could not open source: {source}'
                return
            if self.model is None:
                self.status = 'Loading model...'
                self.model = YOLO(rs.MODEL_PATH)
            if port:
                self.status = f'Connecting to ESP32 on {port}...'
                rs.ensure_output_dirs()
                gps = rs.GpsReader(port, rs.SERIAL_BAUD)

            damage = deque(maxlen=20)
            last_save, saved = 0.0, 0
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    self.status += '   (end of video)'
                    break
                results = self.model.predict(source=frame, imgsz=640, conf=rs.CONF_THRESHOLD, verbose=False)[0]
                pct = rs.damage_percentage(results, frame.shape)
                damage.append(pct)
                status = f'Road damage: {sum(damage) / len(damage):.2f}%'

                if gps:
                    fix = gps.latest()
                    now = time.time()
                    if results.masks is not None and now - last_save >= rs.DETECTION_COOLDOWN_SEC:
                        lat, lon = fix or (None, None)
                        rs.log_detection(frame, lat, lon, pct)
                        last_save, saved = now, saved + 1
                    gps_txt = f'{fix[0]:.6f}, {fix[1]:.6f}' if fix else 'no fix'
                    status += f'   |   GPS: {gps_txt}   |   Saved: {saved}'

                self.frame = cv2.cvtColor(results.plot(boxes=True), cv2.COLOR_BGR2RGB)
                self.status = status
        except Exception as e:  # show serial/model errors in the window instead of dying silently
            self.status = f'Error: {e}'
        finally:
            cap.release()
            if gps:
                gps.close()
            self.running = False

    def refresh(self):
        frame, self.frame = self.frame, None
        if frame is not None:
            img = Image.fromarray(frame)
            img.thumbnail(DISPLAY_SIZE)
            self.photo = ImageTk.PhotoImage(img)  # keep a reference or Tk drops the image
            self.video.configure(image=self.photo)
        self.info.configure(text=self.status)
        self.start_btn.configure(text='Stop' if self.running else 'Start')
        self.root.after(30, self.refresh)

    def close(self):
        self.running = False
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
