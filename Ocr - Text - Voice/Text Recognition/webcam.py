"""
ESP32-CAM OCR to Text
---------------------
Captures JPEG images from the ESP32-CAM and converts visible text to
editable text using Tesseract OCR.

Controls:
  q / ESC : quit
  s       : save the latest OCR result to recognized_text.txt
  c       : clear the displayed OCR text
  b       : convert latest OCR text to Braille files
  t       : speak latest OCR text aloud

Examples:
  python webcam.py
  python webcam.py --url http://192.168.4.1/cam-hi.jpg
  python webcam.py --psm 6 --interval 0.8
  python webcam.py --tesseract "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
"""

import argparse
import os
import shutil
import time
import urllib.error
import urllib.request

import cv2
import numpy as np
import pytesseract

from braille_converter import convert_to_braille
from text_to_voice import speak_text


DEFAULT_URL = "http://192.168.4.1/cam-hi.jpg"
DEFAULT_OUTPUT = "recognized_text.txt"
DEFAULT_BRAILLE_OUTPUT = "braille_text.txt"
DEFAULT_DOTS_OUTPUT = "braille_dots.txt"


def find_tesseract():
    """Find Tesseract automatically on Windows/Linux/macOS."""
    executable = shutil.which("tesseract")
    if executable:
        return executable

    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/opt/homebrew/bin/tesseract",
    ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    return None


def download_frame(url, timeout=5):
    """Download one JPEG frame from the ESP32-CAM."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ESP32-CAM-OCR/1.0"},
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()

    image = cv2.imdecode(
        np.frombuffer(data, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError("ESP32-CAM returned invalid JPEG data.")

    return image


def preprocess_for_ocr(frame):
    """
    Prepare the camera image for OCR.

    ESP32-CAM images are relatively small, so the image is enlarged before
    OCR. Grayscale + contrast enhancement + adaptive thresholding improves
    recognition for printed black text on a light background.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Enlarge small characters.
    scale = 2.0
    gray = cv2.resize(
        gray,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )

    # Reduce sensor noise without destroying character edges.
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Improve local contrast.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Make text easier for Tesseract to separate from the background.
    binary = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return binary


def clean_text(text):
    """Normalize OCR output while preserving separate lines."""
    lines = []
    for line in text.splitlines():
        line = " ".join(line.split())
        if line:
            lines.append(line)

    return "\n".join(lines)


def extract_text(frame, psm=6):
    """Run Tesseract OCR and return cleaned text."""
    processed = preprocess_for_ocr(frame)

    config = f"--oem 3 --psm {psm}"
    text = pytesseract.image_to_string(processed, config=config)

    return clean_text(text), processed


def draw_text_panel(frame, text):
    """Draw a readable OCR result panel on the live camera window."""
    display = frame.copy()

    panel_height = min(
        max(90, 35 + 28 * len(text.splitlines())),
        display.shape[0] // 2,
    )

    overlay = display.copy()
    cv2.rectangle(
        overlay,
        (0, 0),
        (display.shape[1], panel_height),
        (0, 0, 0),
        -1,
    )
    display = cv2.addWeighted(overlay, 0.70, display, 0.30, 0)

    y = 28
    lines = text.splitlines() if text else ["No text detected"]

    for line in lines[:12]:
        # Prevent very long OCR lines from going outside the window.
        line = line[:95]
        cv2.putText(
            display,
            line,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        y += 25

    return display


def save_text(text, output_file):
    """Save OCR result as UTF-8 text."""
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text.strip() + ("\n" if text.strip() else ""))


def main():
    parser = argparse.ArgumentParser(
        description="Convert text seen by an ESP32-CAM into editable text."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"ESP32-CAM JPEG URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--tesseract",
        default=None,
        help="Full path to tesseract.exe/binary. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output text file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--braille-output",
        default=DEFAULT_BRAILLE_OUTPUT,
        help=f"Braille Unicode output file (default: {DEFAULT_BRAILLE_OUTPUT}).",
    )
    parser.add_argument(
        "--dots-output",
        default=DEFAULT_DOTS_OUTPUT,
        help=f"Braille dot-number output file (default: {DEFAULT_DOTS_OUTPUT}).",
    )
    parser.add_argument(
        "--psm",
        type=int,
        default=6,
        choices=range(14),
        help="Tesseract page segmentation mode, 0-13 (default: 6).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.8,
        help="Seconds between OCR operations (default: 0.8).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5,
        help="ESP32-CAM HTTP timeout in seconds (default: 5).",
    )
    args = parser.parse_args()

    tesseract_path = args.tesseract or find_tesseract()

    if not tesseract_path:
        print("ERROR: Tesseract OCR was not found.")
        print("Install Tesseract and make sure 'tesseract' is in PATH,")
        print("or run with --tesseract <full-path-to-tesseract>.")
        return 1

    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    try:
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract: {version}")
    except Exception as exc:
        print(f"ERROR: Tesseract could not be started: {exc}")
        return 1

    print(f"ESP32-CAM: {args.url}")
    print(f"Text file: {os.path.abspath(args.output)}")
    print()
    print("Controls: Q/ESC = quit | S = save text | B = Braille | T = speak text | C = clear text")

    cv2.namedWindow("ESP32-CAM OCR", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ESP32-CAM OCR", 1000, 750)

    latest_text = ""
    last_ocr_time = 0.0
    last_frame = None
    connection_error_shown = False

    while True:
        try:
            frame = download_frame(args.url, args.timeout)
            last_frame = frame
            connection_error_shown = False
        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
            ValueError,
        ) as exc:
            if not connection_error_shown:
                print(f"Camera connection error: {exc}")
                print("Check Wi-Fi connection and the ESP32-CAM IP address.")
                connection_error_shown = True

            if last_frame is None:
                time.sleep(0.5)
                continue

            frame = last_frame.copy()

        now = time.monotonic()

        if now - last_ocr_time >= max(0.1, args.interval):
            try:
                latest_text, _ = extract_text(frame, args.psm)
                last_ocr_time = now

                if latest_text:
                    print("\n--- OCR TEXT ---")
                    print(latest_text)
                    print("----------------")
            except Exception as exc:
                print(f"OCR error: {exc}")

        display = draw_text_panel(frame, latest_text)
        cv2.imshow("ESP32-CAM OCR", display)

        key = cv2.waitKey(1) & 0xFF

        if key in (ord("q"), ord("Q"), 27):
            break

        if key in (ord("s"), ord("S")):
            save_text(latest_text, args.output)
            print(f"Saved OCR text to: {os.path.abspath(args.output)}")

        if key in (ord("b"), ord("B")):
            if latest_text.strip():
                braille_text, dot_text = convert_to_braille(latest_text)
                save_text(braille_text, args.braille_output)
                save_text(dot_text, args.dots_output)
                print("\n--- BRAILLE ---")
                print(braille_text)
                print("--- DOT NUMBERS ---")
                print(dot_text)
                print(f"Saved Braille to: {os.path.abspath(args.braille_output)}")
                print(f"Saved dot notation to: {os.path.abspath(args.dots_output)}")
            else:
                print("No OCR text available for Braille conversion.")

        if key in (ord("t"), ord("T")):
            if latest_text.strip():
                try:
                    print("Speaking OCR text...")
                    speak_text(latest_text)
                except Exception as exc:
                    print(f"Text-to-speech error: {exc}")
            else:
                print("No OCR text available for speech.")

        if key in (ord("c"), ord("C")):
            latest_text = ""

    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
