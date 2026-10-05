# Text to Voice

This project now converts OCR text into spoken audio using **pyttsx3**. Speech is generated locally, so an internet connection is not required after the required voice engine is installed.

## Install
```bash
pip install -r requirements.txt
```

## Standalone converter
Speak typed text:
```bash
python text_to_voice.py "Hello, welcome"
```

Speak OCR output saved in a file:
```bash
python text_to_voice.py --file recognized_text.txt
```

List installed voices:
```bash
python text_to_voice.py --list-voices
```

Select a voice and speech rate:
```bash
python text_to_voice.py --file recognized_text.txt --voice 0 --rate 150
```

## Integrated ESP32-CAM workflow
Run:
```bash
python webcam.py
```
Then press **T** to speak the latest OCR result aloud.

Flow:
**ESP32-CAM → OCR → Text → Text-to-Speech**

### Windows
`pyttsx3` normally uses the installed Windows SAPI voices. If no voice is available, install/enable a Windows speech language/voice in Windows Settings.

### Linux
Install a speech engine such as `espeak-ng` if your system does not already provide one.
