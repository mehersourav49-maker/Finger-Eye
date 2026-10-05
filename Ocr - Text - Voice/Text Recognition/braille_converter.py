"""Convert English Grade-1 text to Braille Unicode and dot-number notation."""

import argparse
from pathlib import Path
import sys

LETTER_DOTS = {
    "a": (1,), "b": (1, 2), "c": (1, 4), "d": (1, 4, 5),
    "e": (1, 5), "f": (1, 2, 4), "g": (1, 2, 4, 5), "h": (1, 2, 5),
    "i": (2, 4), "j": (2, 4, 5), "k": (1, 3), "l": (1, 2, 3),
    "m": (1, 3, 4), "n": (1, 3, 4, 5), "o": (1, 3, 5), "p": (1, 2, 3, 4),
    "q": (1, 2, 3, 4, 5), "r": (1, 2, 3, 5), "s": (2, 3, 4),
    "t": (2, 3, 4, 5), "u": (1, 3, 6), "v": (1, 2, 3, 6),
    "w": (2, 4, 5, 6), "x": (1, 3, 4, 6), "y": (1, 3, 4, 5, 6),
    "z": (1, 3, 5, 6),
}
DIGIT_LETTER = {"1":"a", "2":"b", "3":"c", "4":"d", "5":"e",
                "6":"f", "7":"g", "8":"h", "9":"i", "0":"j"}
PUNCT_DOTS = {
    ",": (2,), ";": (2, 3), ":": (2, 5), ".": (2, 5, 6),
    "!": (2, 3, 5), "?": (2, 3, 6), "'": (3,), "-": (3, 6),
    "(": (2, 3, 5, 6), ")": (2, 3, 5, 6), '"': (2, 3, 6), "/": (3, 4),
}
NUMBER_SIGN = (3, 4, 5, 6)
CAPITAL_SIGN = (6,)


def dots_to_unicode(dots):
    value = 0
    for dot in dots:
        value |= 1 << (dot - 1)
    return chr(0x2800 + value)


def dots_to_text(dots):
    return "-" if not dots else "-".join(str(d) for d in dots)


def convert_to_braille(text):
    """Return (Unicode Braille, dot-number notation)."""
    unicode_parts, dot_parts = [], []
    number_mode = False

    for char in text:
        if char == "\n":
            unicode_parts.append("\n")
            dot_parts.append("\n")
            number_mode = False
        elif char.isspace():
            unicode_parts.append(" ")
            dot_parts.append(" ")
            number_mode = False
        elif char.isdigit():
            if not number_mode:
                unicode_parts.append(dots_to_unicode(NUMBER_SIGN))
                dot_parts.append(f"[{dots_to_text(NUMBER_SIGN)}]")
                number_mode = True
            dots = LETTER_DOTS[DIGIT_LETTER[char]]
            unicode_parts.append(dots_to_unicode(dots))
            dot_parts.append(f"[{dots_to_text(dots)}]")
        elif char.isalpha() and char.lower() in LETTER_DOTS:
            number_mode = False
            dots = LETTER_DOTS[char.lower()]
            if char.isupper():
                unicode_parts.append(dots_to_unicode(CAPITAL_SIGN))
                dot_parts.append(f"[{dots_to_text(CAPITAL_SIGN)}]")
            unicode_parts.append(dots_to_unicode(dots))
            dot_parts.append(f"[{dots_to_text(dots)}]")
        elif char in PUNCT_DOTS:
            number_mode = False
            dots = PUNCT_DOTS[char]
            unicode_parts.append(dots_to_unicode(dots))
            dot_parts.append(f"[{dots_to_text(dots)}]")
        else:
            number_mode = False
            unicode_parts.append("?")
            dot_parts.append(f"[?:{char}]")

    return "".join(unicode_parts), "".join(dot_parts)


def main():
    parser = argparse.ArgumentParser(description="Convert English text to Braille.")
    parser.add_argument("text", nargs="?", help="Text to convert.")
    parser.add_argument("--input", help="Read UTF-8 text from a file.")
    parser.add_argument("--output", default="braille_text.txt")
    parser.add_argument("--dots-output", default="braille_dots.txt")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    elif args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()

    unicode_braille, dot_notation = convert_to_braille(text)
    Path(args.output).write_text(unicode_braille, encoding="utf-8")
    Path(args.dots_output).write_text(dot_notation, encoding="utf-8")

    print("--- BRAILLE UNICODE ---")
    print(unicode_braille)
    print("\n--- BRAILLE DOT NUMBERS ---")
    print(dot_notation)
    print(f"\nSaved Unicode Braille to: {Path(args.output).resolve()}")
    print(f"Saved dot notation to: {Path(args.dots_output).resolve()}")


if __name__ == "__main__":
    main()
