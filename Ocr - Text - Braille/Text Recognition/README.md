# ESP32-CAM OCR to Text

This project uses an **ESP32-CAM** to capture an image and a computer running Python + Tesseract OCR to convert the visible text into editable text.

The ESP32-CAM does the image capture. OCR runs on the connected computer because Tesseract is too large to run directly on a typical ESP32-CAM.

## Features

- ESP32-CAM captures high-resolution JPEG images.
- Python automatically connects to the ESP32-CAM JPEG endpoint.
- Image preprocessing improves OCR accuracy:
  - grayscale conversion
  - 2x image enlargement
  - Gaussian noise reduction
  - CLAHE contrast enhancement
  - adaptive thresholding
- Tesseract converts the processed image into text.
- OCR text is shown live in the camera window.
- Press **S** to save the latest recognized text to `recognized_text.txt`.
- Press **C** to clear the displayed text.
- Press **Q** or **ESC** to exit.
- Tesseract path is automatically detected on Windows, Linux and macOS.
- Camera URL, OCR mode, OCR interval and output file can be changed from the command line.

## Hardware

- ESP32-CAM AI Thinker
- USB-to-TTL programmer for uploading the firmware
- Computer for running Python OCR
- Wi-Fi

## 1. Upload the ESP32-CAM code

Open the folder:

```text
Text Recognition/
```

Use PlatformIO and upload:

```text
src/main.cpp
```

The ESP32-CAM starts a Wi-Fi access point with:

```text
SSID: esp32cam_color
Password: 12345678
```

After connecting your computer to that Wi-Fi network, open the Serial Monitor at **115200 baud**.

The ESP32-CAM prints its AP IP address, normally:

```text
http://192.168.4.1
```

The high-resolution JPEG endpoint is:

```text
http://192.168.4.1/cam-hi.jpg
```

## 2. Install Python dependencies

From the `Text Recognition` directory:

```bash
python -m pip install -r requirements.txt
```

## 3. Install Tesseract OCR

### Windows

Install Tesseract OCR. The program is commonly installed at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The Python program automatically checks this location.

If Tesseract is installed elsewhere, pass its path:

```bash
python webcam.py --tesseract "C:\path\to\tesseract.exe"
```

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install tesseract-ocr
python -m pip install -r requirements.txt
```

### macOS

With Homebrew:

```bash
brew install tesseract
python3 -m pip install -r requirements.txt
```

## 4. Run OCR

Connect the computer to the ESP32-CAM Wi-Fi network and run:

```bash
python webcam.py
```

If the ESP32-CAM has a different IP address:

```bash
python webcam.py --url http://192.168.4.1/cam-hi.jpg
```

You can also change the OCR interval:

```bash
python webcam.py --interval 1.0
```

The OCR result is printed in the terminal and displayed over the live camera image.

## 5. Save recognized text

While the OCR window is open:

```text
S = save latest OCR result
```

The text is saved as:

```text
recognized_text.txt
```

## 6. Convert OCR text to Braille

The project now includes `braille_converter.py`. It converts English text into both Unicode Braille and explicit Braille dot-number notation.

Convert the saved OCR text directly:

```bash
python braille_converter.py --input recognized_text.txt
```

This creates:

```text
braille_text.txt   # Unicode Braille symbols
braille_dots.txt   # dot-number notation such as [1][12][14]
```

You can also convert text directly:

```bash
python braille_converter.py "Hello 123"
```

### Live OCR to Braille

While `webcam.py` is running, press **B** to convert the latest OCR result. The program creates both Braille output files automatically.

Braille dot numbering follows the standard six-dot layout:

```text
1 4
2 5
3 6
```

For example, the letter `A` is dot `1`, represented as `⠁`. The number sign is dots `3-4-5-6`.

The file uses UTF-8 encoding, so it can be opened and edited in normal text editors.

## OCR configuration

The default Tesseract page segmentation mode is:

```text
--psm 6
```

This works well when the camera is pointed at a block of printed text.

For a single line of text:

```bash
python webcam.py --psm 7
```

For a sparse document where text can appear in different positions:

```bash
python webcam.py --psm 11
```

## Important accuracy tips

For better OCR results:

1. Use the `/cam-hi.jpg` endpoint.
2. Keep the text inside the camera frame.
3. Hold the ESP32-CAM steady.
4. Use good lighting.
5. Avoid reflections and shadows.
6. Keep the text reasonably large in the image.
7. For documents, place the camera approximately perpendicular to the page.

The OCR is performed on the computer, not inside the ESP32-CAM.

## Project structure

```text
Text Recognition/
├── src/
│   └── main.cpp
├── lib/
│   ├── Camera Configuration/
│   └── esp32cam-main/
├── webcam.py
├── braille_converter.py
├── requirements.txt
├── platformio.ini
└── README.md
```

## Keyboard controls

| Key | Function |
|---|---|
| Q / ESC | Exit |
| S | Save recognized text |
| B | Convert latest OCR text to Braille |
| C | Clear displayed text |

## Command-line options

```text
--url          ESP32-CAM JPEG URL
--tesseract    Tesseract executable path
--output       OCR output text file
--psm          Tesseract page segmentation mode
--interval     Time between OCR operations
--timeout      Camera HTTP timeout
```

Example:

```bash
python webcam.py ^
  --url http://192.168.4.1/cam-hi.jpg ^
  --psm 6 ^
  --interval 0.8 ^
  --output recognized_text.txt
```

On Linux/macOS, replace `^` with `\` or run the command on one line.

## Architecture

```text
Printed Text
     |
     v
ESP32-CAM
     |
     | JPEG over Wi-Fi
     v
Python + OpenCV
     |
     | Image preprocessing
     v
Tesseract OCR
     |
     v
Recognized Text
     |
     +----> Live display
     |
     +----> recognized_text.txt
```

## License

MIT License. See `LICENSE`.
