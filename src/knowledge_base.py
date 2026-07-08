SIGN_LANGUAGE_GLOSSARY = {
    "hello": "Wave hand with palm facing outward",
    "thank you": "Touch chin with fingertips and move hand forward",
    "yes": "Make a fist and nod it up and down like a head nod",
    "no": "Tap thumb with first two fingers",
    "please": "Rub chest in circular motion with flat hand",
    "sorry": "Make a fist and rub it in a circular motion on chest",
    "help": "Thumbs up on flat palm, lift both hands up",
    "water": "W handshape taps chin",
    "eat": "Fingertips of flat hand tap mouth",
    "good": "Flat hand starts at chin and moves down to chest",
}


def lookup_sign(term: str) -> str:
    return SIGN_LANGUAGE_GLOSSARY.get(term.lower(), f"No sign found for '{term}'")


def get_all_signs() -> dict:
    return SIGN_LANGUAGE_GLOSSARY
