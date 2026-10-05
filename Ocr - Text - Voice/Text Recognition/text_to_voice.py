"""Offline Text-to-Speech converter for the ESP32-CAM OCR project."""

import argparse
import os
import pyttsx3


def list_voices():
    engine = pyttsx3.init()
    for i, voice in enumerate(engine.getProperty("voices")):
        print(f"{i}: {voice.name} | {voice.id}")
    engine.stop()


def speak_text(text, rate=165, volume=1.0, voice_index=None):
    if not text.strip():
        print("No text to speak.")
        return
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", max(0.0, min(1.0, volume)))
    voices = engine.getProperty("voices")
    if voice_index is not None:
        if voice_index < 0 or voice_index >= len(voices):
            engine.stop()
            raise ValueError(f"Voice index must be between 0 and {len(voices)-1}.")
        engine.setProperty("voice", voices[voice_index].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def main():
    parser = argparse.ArgumentParser(description="Convert text to speech offline.")
    parser.add_argument("text", nargs="?", help="Text to speak. If omitted, use --file.")
    parser.add_argument("--file", help="UTF-8 text file to read and speak.")
    parser.add_argument("--rate", type=int, default=165, help="Speech rate, default 165.")
    parser.add_argument("--volume", type=float, default=1.0, help="Volume from 0.0 to 1.0.")
    parser.add_argument("--voice", type=int, help="Voice index; use --list-voices first.")
    parser.add_argument("--list-voices", action="store_true", help="List installed voices and exit.")
    args = parser.parse_args()

    if args.list_voices:
        list_voices()
        return 0

    if args.file:
        if not os.path.isfile(args.file):
            print(f"File not found: {args.file}")
            return 1
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.text or input("Enter text: ")

    speak_text(text, args.rate, args.volume, args.voice)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
