"""
Live pothole road survey: webcam + YOLO segmentation + ESP32 GPS over USB serial.
On pothole detection, saves a geotagged image and logs a CSV row.

ESP32 must send one JSON line per fix over serial, e.g.:
    {"lat": 12.345678, "lon": 77.123456}

Run:  python road_survey.py
Self-check (no hardware needed): python road_survey.py --selftest
"""
import os
import sys
import csv
import json
import time
import threading
from datetime import datetime

import cv2
import numpy as np
import serial
from ultralytics import YOLO

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, 'model', 'best.pt')

OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'survey_output')
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')
CSV_PATH = os.path.join(OUTPUT_DIR, 'survey_log.csv')

SERIAL_PORT = 'COM3'
SERIAL_BAUD = 115200

CAMERA_INDEX = 0
CONF_THRESHOLD = 0.25
DETECTION_COOLDOWN_SEC = 2.0  # min gap between saved detections, avoids flooding disk


def parse_gps_line(line):
    """Parse one JSON line from ESP32 into (lat, lon), or None if invalid/no fix."""
    try:
        data = json.loads(line)
        lat, lon = float(data['lat']), float(data['lon'])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
    if lat == 0.0 and lon == 0.0:
        return None  # common "no fix yet" sentinel
    return (lat, lon)


class GpsReader:
    """Background thread keeping the latest GPS fix from the ESP32 serial line."""

    def __init__(self, port, baud):
        self._lock = threading.Lock()
        self._latest = None
        self._stop = threading.Event()
        self._ser = serial.Serial(port, baud, timeout=1)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            try:
                raw = self._ser.readline().decode('utf-8', errors='ignore').strip()
            except serial.SerialException:
                break
            if not raw:
                continue
            fix = parse_gps_line(raw)
            if fix:
                with self._lock:
                    self._latest = fix

    def latest(self):
        with self._lock:
            return self._latest

    def close(self):
        self._stop.set()
        self._ser.close()


def ensure_output_dirs():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'w', newline='') as f:
            csv.writer(f).writerow(
                ['timestamp', 'latitude', 'longitude', 'image_path', 'damage_percent']
            )


def log_detection(frame, lat, lon, damage_percent):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    lat_s = f'{lat:.6f}' if lat is not None else 'NOFIX'
    lon_s = f'{lon:.6f}' if lon is not None else 'NOFIX'
    filename = f'pothole_{ts}_{lat_s}_{lon_s}.jpg'
    image_path = os.path.join(IMAGES_DIR, filename)
    cv2.imwrite(image_path, frame)
    with open(CSV_PATH, 'a', newline='') as f:
        csv.writer(f).writerow(
            [ts, lat if lat is not None else '', lon if lon is not None else '',
             os.path.join('images', filename), f'{damage_percent:.2f}']
        )
    print(f'[SAVED] {filename}  lat={lat_s} lon={lon_s}  damage={damage_percent:.2f}%')


def damage_percentage(results, frame_shape):
    if results.masks is None:
        return 0.0
    total_area = 0
    image_area = frame_shape[0] * frame_shape[1]
    for mask in results.masks.data.cpu().numpy():
        binary_mask = (mask > 0).astype(np.uint8) * 255
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            total_area += cv2.contourArea(contours[0])
    return (total_area / image_area) * 100


def run_survey():
    ensure_output_dirs()

    print(f'Loading model: {MODEL_PATH}')
    model = YOLO(MODEL_PATH)

    print(f'Connecting to ESP32 on {SERIAL_PORT} @ {SERIAL_BAUD}...')
    gps = GpsReader(SERIAL_PORT, SERIAL_BAUD)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f'ERROR: could not open camera index {CAMERA_INDEX}')
        gps.close()
        return

    last_save = 0.0
    print('Survey running. Press Q to stop.')
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model.predict(source=frame, imgsz=640, conf=CONF_THRESHOLD, verbose=False)[0]
            annotated = results.plot(boxes=True)

            pothole_found = results.masks is not None
            now = time.time()
            if pothole_found and (now - last_save) >= DETECTION_COOLDOWN_SEC:
                lat_lon = gps.latest()
                lat, lon = lat_lon if lat_lon else (None, None)
                damage_pct = damage_percentage(results, frame.shape)
                log_detection(frame, lat, lon, damage_pct)
                last_save = now

            cv2.imshow('Road Survey', annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        gps.close()
        cv2.destroyAllWindows()


def _selftest():
    assert parse_gps_line('{"lat": 12.34, "lon": 56.78}') == (12.34, 56.78)
    assert parse_gps_line('{"lat": 0, "lon": 0}') is None  # no-fix sentinel
    assert parse_gps_line('garbage') is None
    assert parse_gps_line('{"lat": 12.34}') is None  # missing lon
    assert parse_gps_line('') is None
    print('selftest OK')


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
    else:
        run_survey()
